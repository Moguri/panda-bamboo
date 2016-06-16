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
