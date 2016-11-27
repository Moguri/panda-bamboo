#version 130
#ifndef MAX_LIGHTS
#define MAX_LIGHTS 16
#endif


uniform sampler2D p3d_Texture0;
uniform struct p3d_LightSourceParameters {
    vec4 color;
    vec4 position;
} p3d_LightSource[MAX_LIGHTS];

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
    float roughness = 0.4;
    float metallic = 0.0;
    vec3 diffuse = vec3(0.0);
    vec3 spec = vec3(0.0);
    vec3 cspec = vec3(0.04);

    for (int i = 0; i < MAX_LIGHTS; ++i) {
        vec3 L = p3d_LightSource[i].position.xyz - vertex.xyz;
        float dist = length(L);
        L = normalize(L);
        vec3 H = normalize(L + normalize(-V));
        float lambert = max(dot(N, L), 0.0);
        float attenuation = 30.0 / (30.0 + dist * dist);
        vec3 clight = attenuation * lambert * p3d_LightSource[i].color.rgb;

        diffuse += clight;
        vec3 tspec = fresnel(cspec, L, H);
        tspec *= clight;
        tspec *= distf(roughness, N, H);
        tspec *= vis(roughness, N, L, normalize(-V));

        spec += tspec;
    }

    o_color = vec4(base_color * diffuse + spec, 1.0);
}
