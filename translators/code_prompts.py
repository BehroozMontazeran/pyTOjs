import dataclasses
import dataclasses
from enum import auto, Enum
from typing import List, Tuple


class CoderPrompts:
    # code prompts templates
    jinja2_template = "Resume the main objective about this function {python_code}"

    files_content_gpt_edits_no_repo = "I updated the files."

    translate_to_javascript = "translate the following python code to JavaScript:\n\n{python_code}"

    unittest_prompter_statement = "write a unittest for the following python code:\n\n{python_code}"

    py_to_js_error_statement = "The javascript code you provided raises an error. Change the included js code in order not to raise the following included error.\nIncluded js code:\n\n{js_code}\n\nIncluded error: {error}"

    py_unittest_statement = "The unit test code you provided raises an error. Change the included unit test code in order not to raise the following included error.\nIncluded unittest code:\n\n{py_unittest}\n\nIncluded error: {error}"

    correct_error = "The javascript code you provided raises an error. Change the included js code in order not to raise the following included error.\nIncluded js code:\n\n{js_code}\n\nIncluded error: {error}"

    function_summerizing = "Summerize this function {python_code}"

    translate_py_to_js_statement = "Translate the following Python unit test code to JavaScript unit test:\n\n{python_code}"

    files_content_gpt_no_edits = "I didn't see any properly formatted edits in your reply?!"

    files_content_local_edits = "I edited the files myself."


class SeparatorStyle(Enum):
    """Different separator style."""
    SINGLE = auto()
    TWO = auto()
    MPT = auto()
    PLAIN = auto()
    LLAMA_2 = auto()


@dataclasses.dataclass
class Conversation:
    """A class that keeps all conversation history."""
    system: str
    roles: List[str]
    messages: List[List[str]]
    offset: int
    sep_style: SeparatorStyle = SeparatorStyle.SINGLE
    sep: str = "###"
    sep2: str = None
    version: str = "Unknown"

    skip_next: bool = False

    def get_prompt(self):
        messages = self.messages
        if len(messages) > 0 and type(messages[0][1]) is tuple:
            messages = self.messages.copy()
            init_role, init_msg = messages[0].copy()
            init_msg = init_msg[0].replace("<image>", "").strip()
            if 'mmtag' in self.version:
                messages[0] = (init_role, init_msg)
                messages.insert(0, (self.roles[0], "<Image><image></Image>"))
                messages.insert(1, (self.roles[1], "Received."))
            else:
                messages[0] = (init_role, "<image>\n" + init_msg)

        if self.sep_style == SeparatorStyle.SINGLE:
            ret = self.system + self.sep
            for role, message in messages:
                if message:
                    if type(message) is tuple:
                        message, _, _ = message
                    ret += role + ": " + message + self.sep
                else:
                    ret += role + ":"
        elif self.sep_style == SeparatorStyle.TWO:
            seps = [self.sep, self.sep2]
            ret = self.system + seps[0]
            for i, (role, message) in enumerate(messages):
                if message:
                    if type(message) is tuple:
                        message, _, _ = message
                    ret += role + ": " + message + seps[i % 2]
                else:
                    ret += role + ":"
        elif self.sep_style == SeparatorStyle.MPT:
            ret = self.system + self.sep
            for role, message in messages:
                if message:
                    if type(message) is tuple:
                        message, _, _ = message
                    ret += role + message + self.sep
                else:
                    ret += role
        elif self.sep_style == SeparatorStyle.LLAMA_2:
            wrap_sys = lambda msg: f"<<SYS>>\n{msg}\n<</SYS>>\n\n"
            wrap_inst = lambda msg: f"[INST] {msg} [/INST]"
            ret = ""

            for i, (role, message) in enumerate(messages):
                if i == 0:
                    assert message, "first message should not be none"
                    assert role == self.roles[0], "first message should come from user"
                if message:
                    if type(message) is tuple:
                        message, _, _ = message
                    if i == 0: message = wrap_sys(self.system) + message
                    if i % 2 == 0:
                        message = wrap_inst(message)
                        ret += self.sep + message
                    else:
                        ret += " " + message + " " + self.sep2
                else:
                    ret += ""
            ret = ret.lstrip(self.sep)
        elif self.sep_style == SeparatorStyle.PLAIN:
            seps = [self.sep, self.sep2]
            ret = self.system
            for i, (role, message) in enumerate(messages):
                if message:
                    if type(message) is tuple:
                        message, _, _ = message
                    ret += message + seps[i % 2]
                else:
                    ret += ""
        else:
            raise ValueError(f"Invalid style: {self.sep_style}")

        return ret

    def append_message(self, role, message):
        self.messages.append([role, message])

conv_vicuna_v0 = Conversation(
    system="Act as an expert software developer."+
            "Take requests for changes to the supplied code.\n"+
            "If the request is ambiguous, ask questions.\n"+
            "Once you understand the request you MUST use the `write_file` function to update the file to make the changes."
            "The assistant gives helpful, detailed, and polite answers to the human's questions.",
           
    roles=("Human", "Assistant"),

    messages=(
        ("system", "You are an expert programmer, skilled in clean code best practices, translating python to javascript and writing unit tests to check both programming languages"),
    ),
    offset=2,
    sep_style=SeparatorStyle.SINGLE,
    sep="###",
)

conv_vicuna_v1 = Conversation(
    system="A chat between a curious user and an artificial intelligence assistant. "
    "The assistant gives helpful, detailed, and polite answers to the user's questions.",
    roles=("USER", "ASSISTANT"),
    version="v1",
    messages=(
    ),
    offset=0,
    sep_style=SeparatorStyle.TWO,
    sep=" ",
    sep2="</s>",
)


conv_llava_llama_2 = Conversation(
    system="You are a helpful language and vision assistant. "
           "You are able to understand the visual content that the user provides, "
           "and assist the user with a variety of tasks using natural language.",
    roles=("USER", "ASSISTANT"),
    version="llama_v2",
    messages=(),
    offset=0,
    sep_style=SeparatorStyle.LLAMA_2,
    sep="<s>",
    sep2="</s>",
)

conv_mpt = Conversation(
    system="""<|im_start|>system
A conversation between a user and an LLM-based AI assistant. The assistant gives helpful and honest answers.""",
    roles=("<|im_start|>user\n", "<|im_start|>assistant\n"),
    version="mpt",
    messages=(),
    offset=0,
    sep_style=SeparatorStyle.MPT,
    sep="<|im_end|>",
)

conv_llava_plain = Conversation(
    system="",
    roles=("", ""),
    messages=(
    ),
    offset=0,
    sep_style=SeparatorStyle.PLAIN,
    sep="\n",
)

conv_llava_v0 = Conversation(
    system="A chat between a curious human and an artificial intelligence assistant. "
           "The assistant gives helpful, detailed, and polite answers to the human's questions.",
    roles=("Human", "Assistant"),
    messages=(
    ),
    offset=0,
    sep_style=SeparatorStyle.SINGLE,
    sep="###",
)

conv_llava_v0_mmtag = Conversation(
    system="A chat between a curious user and an artificial intelligence assistant. "
           "The assistant is able to understand the visual content that the user provides, and assist the user with a variety of tasks using natural language."
           "The visual content will be provided with the following format: <Image>visual content</Image>.",
    roles=("Human", "Assistant"),
    messages=(
    ),
    offset=0,
    sep_style=SeparatorStyle.SINGLE,
    sep="###",
    version="v0_mmtag",
)

conv_llava_v1 = Conversation(
    system="A chat between a curious human and an artificial intelligence assistant. "
           "The assistant gives helpful, detailed, and polite answers to the human's questions.",
    roles=("USER", "ASSISTANT"),
    version="v1",
    messages=(),
    offset=0,
    sep_style=SeparatorStyle.TWO,
    sep=" ",
    sep2="</s>",
)

conv_llava_v1_mmtag = Conversation(
    system="A chat between a curious user and an artificial intelligence assistant. "
           "The assistant is able to understand the visual content that the user provides, and assist the user with a variety of tasks using natural language."
           "The visual content will be provided with the following format: <Image>visual content</Image>.",
    roles=("USER", "ASSISTANT"),
    messages=(),
    offset=0,
    sep_style=SeparatorStyle.TWO,
    sep=" ",
    sep2="</s>",
    version="v1_mmtag",
)

default_conversation = conv_vicuna_v0
conv_templates = {
    "default": conv_vicuna_v0,
    "v0": conv_vicuna_v0,
    "v1": conv_vicuna_v1,
    "vicuna_v1": conv_vicuna_v1,


    "plain": conv_llava_plain,
    "v0_plain": conv_llava_plain,
    "llava_v0": conv_llava_v0,
    "v0_mmtag": conv_llava_v0_mmtag,
    "llava_v1": conv_llava_v1,
    "v1_mmtag": conv_llava_v1_mmtag,
    "llava_llama_2": conv_llava_llama_2,

    "mpt": conv_mpt,
}




if __name__ == '__main__' : 
    print(conv_templates["vicuna_v1"].get_prompt())