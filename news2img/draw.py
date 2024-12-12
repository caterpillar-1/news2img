"""Draw an image according to the prompt.

Todo:
    * Implement ``DrawAscend``.

"""

class Draw:
    """Providing drawing ability

    Example:
        ::

            prompt: str = "blue sky"
            painter = DrawCpu()
            image = painter(prompt)

    Todo:
        * Check what's the type of image in the example given above.
    """
    def __init__(self):
        pass

    def __call__(self, prompt, **kwargs):
        raise NotImplementedError()

class DrawAscend(Draw):
    pass

class DrawCpu(Draw):
    def __init__(self):
        import torch
        from diffusers import StableDiffusionPipeline
        self._pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", torch_dtype=torch.float16)

    def __call__(self, prompt):
        return self._pipe(prompt).images

__all__ = ['Draw', 'DrawCpu', 'DrawAscend']
