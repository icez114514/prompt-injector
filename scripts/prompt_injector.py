# prompt_injector.py
import re
import time
import gradio as gr
from PIL import Image
import modules.scripts as scripts

# ---------- helpers ----------
def _log(msg):
    print(f"[pi] {time.strftime('%Y-%m-%d %H:%M:%S')} {msg}")

def _safe_get_info_text(img):
    if not img:
        return ""
    try:
        info = img.info or {}
    except Exception:
        return ""
    for key in ("parameters", "Parameters", "prompt", "Prompt", "Text", "description"):
        val = info.get(key)
        if val and isinstance(val, str) and val.strip():
            return val
    return ""

def _truncate_at_steps(text):
    if not text:
        return ""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    m = re.search(r'\n\s*Steps?\s*:\s*\d+', text, flags=re.I)
    if m:
        return text[:m.start()].strip()
    m2 = re.search(r'Steps?\s*:\s*\d+', text, flags=re.I)
    if m2:
        return text[:m2.start()].strip()
    return text.strip()

def _remove_meta_lines(text):
    if not text:
        return ""
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    filtered = []
    for line in lines:
        if not line.strip():
            continue
        if re.match(r'^\s*(Steps?|Sampler|CFG|CFG scale|Seed|Model|Model hash|Size|ETA|Eta)\s*[:=]', line, flags=re.I):
            continue
        filtered.append(line)
    return ' '.join([l.strip() for l in filtered]).strip()

def extract_prompts_from_image(pil_img):
    raw = _safe_get_info_text(pil_img)
    if not raw:
        return "", ""
    truncated = _truncate_at_steps(raw)
    neg = ""
    pos = ""
    if re.search(r'negative\s*prompt\s*:', truncated, flags=re.I):
        parts = re.split(r'\n?negative\s*prompt\s*:\s*', truncated, flags=re.I, maxsplit=1)
        pos = parts[0].strip()
        neg = parts[1].strip() if len(parts) > 1 else ""
    elif re.search(r'\n?negative\s*:\s*', truncated, flags=re.I):
        parts = re.split(r'\n?negative\s*:\s*', truncated, flags=re.I, maxsplit=1)
        pos = parts[0].strip()
        neg = parts[1].strip() if len(parts) > 1 else ""
    else:
        pos = truncated.strip()
        neg = ""
    pos_clean = _remove_meta_lines(pos)
    neg_clean = _remove_meta_lines(neg)
    return pos_clean, neg_clean

def combine_prompt(existing, addition, position):
    existing = str(existing or "").strip()
    addition = str(addition or "").strip()
    if not addition:
        return existing
    if not existing:
        return addition
    if position == "前面":
        return addition + ", " + existing
    else:
        return existing + ", " + addition

# ---------- Script-style UI & logic ----------
class PromptInjectorScript(scripts.Script):
    def __init__(self):
        super().__init__()

        # --- 建立 6 組 UI 元件（類別層級，render=False） ---
        # Image 1
        self.enable1 = gr.Checkbox(label="啟用 Image 1", value=True, render=False, elem_id="pi_enable1")
        self.image1 = gr.Image(type="pil", label="Image 1: 上傳含 prompt metadata 的 PNG", render=False, elem_id="pi_image1")
        self.add_positive1 = gr.Checkbox(label="附加正向 Prompt", value=True, render=False, elem_id="pi_add_pos1")
        self.add_negative1 = gr.Checkbox(label="附加負向 Prompt", value=True, render=False, elem_id="pi_add_neg1")
        self.append_pos1 = gr.Radio(["前面", "後面"], value="後面", label="附加位置", render=False, elem_id="pi_append_pos1")

        # Image 2
        self.enable2 = gr.Checkbox(label="啟用 Image 2", value=False, render=False, elem_id="pi_enable2")
        self.image2 = gr.Image(type="pil", label="Image 2: 上傳含 prompt metadata 的 PNG", render=False, elem_id="pi_image2")
        self.add_positive2 = gr.Checkbox(label="附加正向 Prompt", value=True, render=False, elem_id="pi_add_pos2")
        self.add_negative2 = gr.Checkbox(label="附加負向 Prompt", value=True, render=False, elem_id="pi_add_neg2")
        self.append_pos2 = gr.Radio(["前面", "後面"], value="後面", label="附加位置", render=False, elem_id="pi_append_pos2")

        # Image 3
        self.enable3 = gr.Checkbox(label="啟用 Image 3", value=False, render=False, elem_id="pi_enable3")
        self.image3 = gr.Image(type="pil", label="Image 3: 上傳含 prompt metadata 的 PNG", render=False, elem_id="pi_image3")
        self.add_positive3 = gr.Checkbox(label="附加正向 Prompt", value=True, render=False, elem_id="pi_add_pos3")
        self.add_negative3 = gr.Checkbox(label="附加負向 Prompt", value=True, render=False, elem_id="pi_add_neg3")
        self.append_pos3 = gr.Radio(["前面", "後面"], value="後面", label="附加位置", render=False, elem_id="pi_append_pos3")

        # Image 4
        self.enable4 = gr.Checkbox(label="啟用 Image 4", value=False, render=False, elem_id="pi_enable4")
        self.image4 = gr.Image(type="pil", label="Image 4: 上傳含 prompt metadata 的 PNG", render=False, elem_id="pi_image4")
        self.add_positive4 = gr.Checkbox(label="附加正向 Prompt", value=True, render=False, elem_id="pi_add_pos4")
        self.add_negative4 = gr.Checkbox(label="附加負向 Prompt", value=True, render=False, elem_id="pi_add_neg4")
        self.append_pos4 = gr.Radio(["前面", "後面"], value="後面", label="附加位置", render=False, elem_id="pi_append_pos4")

        # Image 5
        self.enable5 = gr.Checkbox(label="啟用 Image 5", value=False, render=False, elem_id="pi_enable5")
        self.image5 = gr.Image(type="pil", label="Image 5: 上傳含 prompt metadata 的 PNG", render=False, elem_id="pi_image5")
        self.add_positive5 = gr.Checkbox(label="附加正向 Prompt", value=True, render=False, elem_id="pi_add_pos5")
        self.add_negative5 = gr.Checkbox(label="附加負向 Prompt", value=True, render=False, elem_id="pi_add_neg5")
        self.append_pos5 = gr.Radio(["前面", "後面"], value="後面", label="附加位置", render=False, elem_id="pi_append_pos5")

        # Image 6
        self.enable6 = gr.Checkbox(label="啟用 Image 6", value=False, render=False, elem_id="pi_enable6")
        self.image6 = gr.Image(type="pil", label="Image 6: 上傳含 prompt metadata 的 PNG", render=False, elem_id="pi_image6")
        self.add_positive6 = gr.Checkbox(label="附加正向 Prompt", value=True, render=False, elem_id="pi_add_pos6")
        self.add_negative6 = gr.Checkbox(label="附加負向 Prompt", value=True, render=False, elem_id="pi_add_neg6")
        self.append_pos6 = gr.Radio(["前面", "後面"], value="後面", label="附加位置", render=False, elem_id="pi_append_pos6")

        # flag to avoid multiple renders
        self._rendered_once = False

    def title(self):
        return "Prompt Injector from Image"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    # 在負向提示詞元件後面渲染
    def after_component(self, component, **kwargs):
        try:
            if self._rendered_once:
                return

            elem = kwargs.get("elem_id", "")
            if elem in ("txt2img_neg_prompt", "img2img_neg_prompt"):
                with gr.Row():
                    with gr.Column(scale=19):
                        with gr.Accordion("Prompt Injector（從 PNG metadata 注入 prompt）", open=False, elem_id="pi_main_accordion"):
                            gr.Markdown("上傳含有 parameters/Prompt metadata 的 PNG，勾選啟用後生成時會自動把圖片內的正向/負向 prompt 注入到生成參數中。")

                            # Tabs（6 個）
                            with gr.Tabs():
                                with gr.Tab("Image 1"):
                                    self.enable1.render()
                                    self.image1.render()
                                    self.add_positive1.render()
                                    self.add_negative1.render()
                                    self.append_pos1.render()

                                with gr.Tab("Image 2"):
                                    self.enable2.render()
                                    self.image2.render()
                                    self.add_positive2.render()
                                    self.add_negative2.render()
                                    self.append_pos2.render()

                                with gr.Tab("Image 3"):
                                    self.enable3.render()
                                    self.image3.render()
                                    self.add_positive3.render()
                                    self.add_negative3.render()
                                    self.append_pos3.render()

                                with gr.Tab("Image 4"):
                                    self.enable4.render()
                                    self.image4.render()
                                    self.add_positive4.render()
                                    self.add_negative4.render()
                                    self.append_pos4.render()

                                with gr.Tab("Image 5"):
                                    self.enable5.render()
                                    self.image5.render()
                                    self.add_positive5.render()
                                    self.add_negative5.render()
                                    self.append_pos5.render()

                                with gr.Tab("Image 6"):
                                    self.enable6.render()
                                    self.image6.render()
                                    self.add_positive6.render()
                                    self.add_negative6.render()
                                    self.append_pos6.render()

                self._rendered_once = True
        except Exception as e:
            _log(f"after_component exception: {e}")

    def ui(self, is_img2img):
        # 回傳對應 process() 的元件順序（6 組）
        return [
            self.image1, self.enable1, self.add_positive1, self.add_negative1, self.append_pos1,
            self.image2, self.enable2, self.add_positive2, self.add_negative2, self.append_pos2,
            self.image3, self.enable3, self.add_positive3, self.add_negative3, self.append_pos3,
            self.image4, self.enable4, self.add_positive4, self.add_negative4, self.append_pos4,
            self.image5, self.enable5, self.add_positive5, self.add_negative5, self.append_pos5,
            self.image6, self.enable6, self.add_positive6, self.add_negative6, self.append_pos6,
        ]

    def get_prompts_lists(self, p):
        original_prompts = getattr(p, "all_prompts", None)
        if not original_prompts or len(original_prompts) == 0:
            original_prompts = [getattr(p, "prompt", "")]
        original_negative_prompts = getattr(p, "all_negative_prompts", None)
        if not original_negative_prompts or len(original_negative_prompts) == 0:
            original_negative_prompts = [getattr(p, "negative_prompt", "")]
        return original_prompts, original_negative_prompts

    def process(self, p,
                image1, enable1, add_positive1, add_negative1, append_pos1,
                image2, enable2, add_positive2, add_negative2, append_pos2,
                image3, enable3, add_positive3, add_negative3, append_pos3,
                image4, enable4, add_positive4, add_negative4, append_pos4,
                image5, enable5, add_positive5, add_negative5, append_pos5,
                image6, enable6, add_positive6, add_negative6, append_pos6):
        try:
            if getattr(p, "prompt", None) is None:
                p.prompt = ""
            if not hasattr(p, "negative_prompt"):
                setattr(p, "negative_prompt", "")

            orig_prompts, orig_neg_prompts = self.get_prompts_lists(p)

            def inject_into_p(new_pos, new_neg, append_position):
                if new_pos:
                    if isinstance(p.prompt, list):
                        p.prompt = [combine_prompt(item, new_pos, append_position) for item in p.prompt]
                    else:
                        p.prompt = combine_prompt(p.prompt, new_pos, append_position)
                p.all_prompts = [p.prompt] if not isinstance(p.prompt, list) else p.prompt
                p.prompt_for_display = p.all_prompts[0] if isinstance(p.all_prompts, list) and len(p.all_prompts) > 0 else p.prompt
                _log(f"Injected positive (start): '{str(p.prompt)[:200]}'")

                if new_neg:
                    if hasattr(p, "negative_prompt") and isinstance(p.negative_prompt, list):
                        p.negative_prompt = [combine_prompt(item, new_neg, append_position) for item in p.negative_prompt]
                        p.all_negative_prompts = p.negative_prompt
                    else:
                        cur = getattr(p, "negative_prompt", "") or ""
                        new_value = combine_prompt(cur, new_neg, append_position)
                        setattr(p, "negative_prompt", new_value)
                        p.all_negative_prompts = [new_value]
                    _log(f"Injected negative (start): '{str(getattr(p, 'negative_prompt',''))[:200]}'")

            tabs = [
                (image1, enable1, add_positive1, add_negative1, append_pos1),
                (image2, enable2, add_positive2, add_negative2, append_pos2),
                (image3, enable3, add_positive3, add_negative3, append_pos3),
                (image4, enable4, add_positive4, add_negative4, append_pos4),
                (image5, enable5, add_positive5, add_negative5, append_pos5),
                (image6, enable6, add_positive6, add_negative6, append_pos6),
            ]

            for idx, (img, enabled, add_pos, add_neg, append_pos) in enumerate(tabs, start=1):
                try:
                    enabled_flag = bool(enabled)
                except Exception:
                    enabled_flag = False
                if not enabled_flag or img is None:
                    _log(f"Tab {idx}: skipped (enabled={enabled_flag}, img_is_none={img is None})")
                    continue

                try:
                    pos, neg = extract_prompts_from_image(img)
                except Exception as e:
                    _log(f"Tab {idx}: extract_prompts_from_image error: {e}")
                    pos, neg = "", ""

                if not pos and not neg:
                    _log(f"Tab {idx}: no prompts found in image metadata")
                    continue

                _log(f"Tab {idx}: extracted pos(len={len(pos)}): '{(pos[:200]+'...') if len(pos)>200 else pos}' | neg(len={len(neg)}): '{(neg[:200]+'...') if len(neg)>200 else neg}'")

                to_inject_pos = pos if add_pos else ""
                to_inject_neg = neg if add_neg else ""
                inject_into_p(to_inject_pos, to_inject_neg, append_pos)

        except Exception as e:
            _log(f"process top-level exception: {e}")

        return

# modules.scripts 會自動 discover subclass，不需手動註冊
