import os

import panda3d.core as p3d
from direct.filter.FilterManager import FilterManager

if '__file__' in globals():
    shader_dir = os.path.join(os.path.dirname(__file__), 'shaders') + '/'
else:
    import sys
    shader_dir = os.path.join(os.path.dirname(sys.executable), 'bamboo', 'shaders') + '/'
material_shader_sources = [shader_dir + 'common.vs', shader_dir + 'pbr.fs']
post_shader_sources = [shader_dir + 'post.vs', shader_dir + 'post.fs']
antialias_shader_sources = [shader_dir + 'post.vs', shader_dir + 'fxaa.fs']
all_shader_sources = [material_shader_sources, post_shader_sources, antialias_shader_sources]


class BambooRenderManager:
    def __init__(self, base):
        # Load shader sources to avoid model path problems
        for src_set in all_shader_sources:
            for i, filename in enumerate(src_set):
                with open(filename, 'r') as fin:
                    src_set[i] = fin.read()

        base.render.set_shader_auto()
        base.render.set_attrib(p3d.LightRampAttrib.make_identity())
        pbr_shader = p3d.Shader.make(p3d.Shader.SL_GLSL, *material_shader_sources)
        base.render.set_shader(pbr_shader)

        manager = FilterManager(base.win, base.cam)
        aa_tex = p3d.Texture()
        self.post_tex = p3d.Texture()
        self.post_tex.set_component_type(p3d.Texture.T_float)
        aa_quad = manager.renderSceneInto(colortex=self.post_tex)
        post_quad = manager.renderQuadInto(colortex=aa_tex)

        aa_quad.set_shader(p3d.Shader.make(p3d.Shader.SL_GLSL, *antialias_shader_sources))
        aa_quad.set_shader_input('source', aa_tex)
        aa_quad.set_shader_input('viewport', base.win.get_size())

        post_quad.set_shader(p3d.Shader.make(p3d.Shader.SL_GLSL, *post_shader_sources))
        post_quad.set_shader_input('tex', self.post_tex)


def get_plugin():
    return BambooRenderManager

