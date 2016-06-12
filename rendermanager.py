import panda3d.core as p3d
from direct.filter.FilterManager import FilterManager
from direct.filter.CommonFilters import CommonFilters

pbr_vert = """
#version 130

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;

out vec4 vertex;
out vec3 normal;
out vec2 texcoord;

void main() {
    vertex = p3d_ModelViewMatrix * p3d_Vertex;
    normal = p3d_NormalMatrix * p3d_Normal;
    texcoord = p3d_MultiTexCoord0;

    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
"""

pbr_frag = """
#version 130

uniform sampler2D p3d_Texture0;

uniform struct p3d_LightSourceParameters {
    vec4 color;
    vec4 position;
} p3d_LightSource[1];

const int light_count = 1;

in vec4 vertex;
in vec3 normal;
in vec2 texcoord;

out vec4 o_color;

vec3 fresnel(vec3 cspec, vec3 L, vec3 H) {
    // Schlick
    return cspec + (1.0 - cspec) * pow((1.0 - dot(L, H)), 5.0);
}

float distf(float a, vec3 N, vec3 H) {
    // GGX
    float a2 = a * a;
    float NoH2 = pow(dot(N, H), 2.0);
    return a2 / (4.0 * pow((NoH2 * (a2 - 1.0) + 1.0), 2.0));
}

float vis(float a, vec3 N, vec3 L, vec3 V) {
    // Schlick with k = a/2
    float k = pow(a + 1.0, 2.0) / 8.0;
    float NoV = dot(N, V);
    float NoL = dot(N, L);
    float gv = NoV * (1.0 - k) + k;
    float gl = NoL * (1.0 - k) + k;
    return 1.0 / (4.0 * gv * gl);
}

void main() {
    vec3 base_color = texture(p3d_Texture0, texcoord).rgb;
    vec3 N = normalize(normal);
    vec3 V = vertex.xyz;
    float roughness = 0.8;
    float metallic = 0.0;
    vec3 diffuse = vec3(0.0);
    vec3 spec = vec3(0.0);
    vec3 cspec = vec3(0.04);

    for (int i = 0; i < light_count; ++i) {
        vec3 L = p3d_LightSource[0].position.xyz - vertex.xyz;
        float dist = length(L);
        L = normalize(L);
        vec3 H = normalize(L + normalize(-V));
        float lambert = max(dot(normalize(normal), L), 0.0);
        float attenuation = 30.0 / (30.0 + dist * dist);
        vec3 clight = attenuation * lambert * p3d_LightSource[0].color.rgb;

        diffuse += clight;
        vec3 tspec = fresnel(cspec, L, H);
        tspec *= clight;
        tspec *= distf(roughness, N, H);
        tspec *= vis(roughness, N, L, normalize(-V));

        spec += tspec;
    }

    o_color = vec4(base_color * diffuse + spec, 1.0);
}
"""

hdr_vert = """
#version 130

uniform mat4 p3d_ModelViewProjectionMatrix;

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

out vec2 texcoord;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoord = p3d_MultiTexCoord0;
}
"""

# GLSL version of Uncharted 2 operator taken from http://filmicgames.com/archives/75
hdr_frag = """
#version 130

uniform sampler2D tex;

in vec2 texcoord;

out vec4 o_color;

void main() {
    vec3 color = texture(tex, texcoord).rgb;

    color = max(vec3(0.0), color - vec3(0.004));
    color = (color * (vec3(6.2) * color + vec3(0.5))) / (color * (vec3(6.2) * color + vec3(1.7)) + vec3(0.06));

    o_color = vec4(color, 1.0);
}
"""


class BambooRenderManager:
    def __init__(self, base):
        base.render.set_shader_auto()
        base.render.set_attrib(p3d.LightRampAttrib.make_identity())
        pbr_shader = p3d.Shader.make(p3d.Shader.SL_GLSL, pbr_vert, pbr_frag)
        base.render.set_shader(pbr_shader)

        manager = FilterManager(base.win, base.cam)
        tex = p3d.Texture()
        quad = manager.renderSceneInto(colortex=tex)
        quad.set_shader(p3d.Shader.make(p3d.Shader.SL_GLSL, hdr_vert, hdr_frag))
        quad.set_shader_input('tex', tex)


        self.base = base


def get_plugin():
    return BambooRenderManager

