#include "glew.h"
#include "gl.h"
#include <string.h>

GLuint shader_program = 0;

// the following opengl shaders are from theoraplay. I know almost nothing about shaders

static const char *glsl_vertex =
    "#version 110\n"
    "attribute vec2 pos;\n"
    "attribute vec2 tex;\n"
    "void main() {\n"
        "gl_Position = vec4(pos.xy, 0.0, 1.0);\n"
        "gl_TexCoord[0].xy = tex;\n"
    "}\n";

// This shader was originally from SDL 1.3.
static const char *glsl_yuv_fragment =
    "#version 110\n"
    "uniform sampler2D samp0;\n"
    "uniform sampler2D samp1;\n"
    "uniform sampler2D samp2;\n"
    "const vec3 offset = vec3(-0.0625, -0.5, -0.5);\n"
    "const vec3 Rcoeff = vec3(1.164,  0.000,  1.596);\n"
    "const vec3 Gcoeff = vec3(1.164, -0.391, -0.813);\n"
    "const vec3 Bcoeff = vec3(1.164,  2.018,  0.000);\n"
    "void main() {\n"
    "    vec2 tcoord;\n"
    "    vec3 yuv, rgb;\n"
    "    tcoord = gl_TexCoord[0].xy;\n"
    "    yuv.x = texture2D(samp0, tcoord).r;\n"
    "    yuv.y = texture2D(samp1, tcoord).r;\n"
    "    yuv.z = texture2D(samp2, tcoord).r;\n"
    "    yuv += offset;\n"
    "    rgb.r = dot(yuv, Rcoeff);\n"
    "    rgb.g = dot(yuv, Gcoeff);\n"
    "    rgb.b = dot(yuv, Bcoeff);\n"
    "    gl_FragColor = vec4(rgb, 1.0);\n"
    "}\n";



static int init_shaders()
{
    const char *vertexsrc = glsl_vertex;
    const char *fragmentsrc = NULL;
    GLuint vertex = 0;
    GLuint fragment = 0;
    GLuint shader_program = 0;
    GLint ok = 0;
    GLint shaderlen = 0;

	fragmentsrc = glsl_yuv_fragment;
    
    ok = 0;
    shaderlen = (GLint) strlen(vertexsrc);
    vertex = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vertex, 1, (const GLchar **) &vertexsrc, &shaderlen);
    glCompileShader(vertex);
    glGetShaderiv(vertex, GL_COMPILE_STATUS, &ok);
    if (!ok)
    {
        glDeleteShader(vertex);
        return 0;
    } // if

    ok = 0;
    shaderlen = (GLint) strlen(fragmentsrc);
    fragment = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fragment, 1, (const GLchar **) &fragmentsrc, &shaderlen);
    glCompileShader(fragment);
    glGetShaderiv(fragment, GL_COMPILE_STATUS, &ok);
    if (!ok)
    {
        glDeleteShader(fragment);
        return 0;
    } // if

    ok = 0;
    shader_program = glCreateProgram();
    glAttachShader(shader_program, vertex);
    glAttachShader(shader_program, fragment);
    glBindAttribLocation(shader_program, 0, "pos");
    glBindAttribLocation(shader_program, 1, "tex");
    glLinkProgram(shader_program);
    glDeleteShader(vertex);
    glDeleteShader(fragment);
    glGetProgramiv(shader_program, GL_LINK_STATUS, &ok);
    if (!ok)
    {
        glDeleteProgram(shader_program);
        return 0;
    } // if



	glUniform1i(glGetUniformLocation(shader_program, "samp0"), 0);
	glUniform1i(glGetUniformLocation(shader_program, "samp1"), 1);

    return 1;
} // init_shaders

static void prep_texture(GLuint *texture, const int idx)
{
    glActiveTexture(GL_TEXTURE0 + idx);
    glBindTexture(GL_TEXTURE_2D, texture[idx]);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0);
} // prep_texture

void update_tex(char *pixels, int gltex, int w, int h)
{
	GLuint tex = (GLuint)gltex;
	
	// turn on the global yuv shader
	if(shader_program == 0)
		init_shaders();
	
    glUseProgram(shader_program);
    glBindTexture(GL_TEXTURE_2D, tex);
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE, pixels);
	glUseProgram(0);
}
