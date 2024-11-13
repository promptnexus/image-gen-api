from diffusers import DiffusionPipeline
import torch

class DeepFloydCombinedPipeline:
   @classmethod
   def from_pretrained(cls, model_path=None, default_params=None, **kwargs):
       """
       default_params = {
           "stage1": {"variant": "fp16"},
           "stage2": {"text_encoder": None, "variant": "fp16"},
           "stage3": {"some_param": "value"}
       }
       """
       return cls(default_params=default_params or {}, **kwargs)

   def __init__(self, device="cuda", torch_dtype=torch.float16, default_params=None, **kwargs):
       self.device = device
       self.dtype = torch_dtype
       default_params = default_params or {}
       
       # Get stage-specific params
       stage1_params = default_params.get("stage1", {})
       stage2_params = default_params.get("stage2", {})
       stage3_params = default_params.get("stage3", {})
       
       print("Loading stage 1...")
       self.stage_1 = DiffusionPipeline.from_pretrained(
           "DeepFloyd/IF-I-XL-v1.0",
           torch_dtype=self.dtype,
           **stage1_params,
           **kwargs
       )
       
       print("Loading stage 2...")
       self.stage_2 = DiffusionPipeline.from_pretrained(
           "DeepFloyd/IF-II-L-v1.0",
           torch_dtype=self.dtype,
           **stage2_params,
           **kwargs
       )
       
       print("Loading stage 3...")
       safety_modules = {
           "feature_extractor": self.stage_1.feature_extractor,
           "safety_checker": self.stage_1.safety_checker,
           "watermarker": self.stage_1.watermarker
       }
       
       self.stage_3 = DiffusionPipeline.from_pretrained(
           "stabilityai/stable-diffusion-x4-upscaler",
           **safety_modules,
           torch_dtype=self.dtype,
           **stage3_params,
           **kwargs
       )
       
       for stage in [self.stage_1, self.stage_2, self.stage_3]:
           stage.enable_model_cpu_offload()
           stage.enable_xformers_memory_efficient_attention()

   def enable_model_cpu_offload(self):
       for stage in [self.stage_1, self.stage_2, self.stage_3]:
           stage.enable_model_cpu_offload()

   def __call__(self, prompt, **inference_params):
        # Extract generator if it exists in inf params
        generator = inference_params.pop('generator', None)

        prompt_embeds, negative_embeds = self.stage_1.encode_prompt(prompt)

        image = self.stage_1(
            prompt_embeds=prompt_embeds,
            negative_prompt_embeds=negative_embeds,
            generator=generator,
            output_type="pt"
        ).images

        image = self.stage_2(
            image=image,
            prompt_embeds=prompt_embeds,
            negative_prompt_embeds=negative_embeds,
            generator=generator,
            output_type="pt"
        ).images

        # Pass remaining inference_params to stage 3
        return self.stage_3(
            prompt=prompt,
            image=image,
            generator=generator,
            **inference_params
        ).images[0]