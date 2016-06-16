#version 130

uniform sampler2D tex;
uniform sampler2D noise;

in vec2 texcoord;
out vec4 o_color;


void main() {
    vec3 color = texture(tex, texcoord).rgb;

    color = max(vec3(0.0), color - vec3(0.004));
    color = (color * (vec3(6.2) * color + vec3(0.5))) / (color * (vec3(6.2) * color + vec3(1.7)) + vec3(0.06));

    o_color = vec4(color, 1.0);
}
