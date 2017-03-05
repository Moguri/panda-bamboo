#version 130
#ifndef MAX_LIGHTS
#define MAX_LIGHTS 16
#endif

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;
uniform struct p3d_LightSourceParameters {
  mat4 shadowMatrix;
} p3d_LightSource[MAX_LIGHTS];

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;

out vec4 vertex;
out vec3 normal;
out vec2 texcoord;
out vec4 shadowcoord[MAX_LIGHTS];

void main() {
    vertex = p3d_ModelViewMatrix * p3d_Vertex;
    normal = p3d_NormalMatrix * p3d_Normal;
    texcoord = p3d_MultiTexCoord0;

    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    for (int i = 0; i < p3d_LightSource.length(); ++i) {
        shadowcoord[i] = p3d_LightSource[i].shadowMatrix * p3d_Vertex;
    }
}
