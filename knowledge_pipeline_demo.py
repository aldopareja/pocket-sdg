##
import asyncio
import aiohttp
from jinja2 import Template
import re

##
from simple_pocket_flow import AsyncNode, AsyncFlow
async def async_call_llm(prompt):
    messages = [
        {
            "role": "user",
            "content": prompt
        },
    ]
    request_data = {
        "model": "phi4-mini",
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.8,
        "stream": False
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11434/v1/chat/completions",
            json=request_data,
            headers={'Content-Type': 'application/json'},
            timeout=aiohttp.ClientTimeout(total=120)
        ) as response:
            r = await response.json()
            response = [choice["message"]["content"] for choice in r["choices"]][0]
        return response

class DuplicateColumns(AsyncNode):
    async def exec(self, sample):
        sample['base_document'] = sample['document']
        return "default", sample
    
class BaseLLMBlock(AsyncNode):
    async def exec(self, sample):
        prompt_string = await self.get_input(sample)
        if prompt_string == "<|invalid input|>":
            return "end", sample
        print(f"prompt_string: {prompt_string}")
        output_string = await async_call_llm(prompt_string)
        print(f"output_string: {output_string}")
        sample = await self.parse_output(sample, output_string)
        return "default", sample
    
class SimpleInputParse:
    def __init__(self, prompt_template, **kwargs):
        self.prompt_template = Template(prompt_template)
        self.prep_fn = kwargs.get("prep_fn", None)

    async def get_input(self, sample):
        try:
            print(self.prep_fn)
            print(f"sample: {type(sample)}")
            sample_ = self.prep_fn(sample) if self.prep_fn else sample
            sample.update(**sample_)
            input_str = self.prompt_template.render(sample).strip()
            return input_str
        except Exception as e:
            import traceback
            traceback.print_exc()
            return "<|invalid input|>"
    
class SimpleOutParse:
    def __init__(self, output_cols, start_tags=[""], end_tags=[""], **kwargs):
        self.output_cols = output_cols
        self.start_tags = start_tags
        self.end_tags = end_tags

    async def parse_output(self, sample, output_string):
        for start_tag, end_tag, out_col in zip(self.start_tags, self.end_tags, self.output_cols):
            if not start_tag and not end_tag:
                sample[out_col] = output_string
            else:
                raise NotImplementedError
            return sample

class CustomOutParse:
    def __init__(self, output_cols, parsing_pattern, parser_cleanup_tags, **kwargs):
        self.output_cols = output_cols
        self.parsing_pattern = parsing_pattern
        self.parser_cleanup_tags = parser_cleanup_tags

    async def parse_output(self, sample, output_string):
        # print(f"output_string: {output_string}")
        sample['debug_output_string'] = output_string
        pattern = re.compile(self.parsing_pattern, re.DOTALL)
        all_matches = pattern.findall(output_string)
        sample.update({column_name: [] for column_name in self.output_cols})
        if all_matches and isinstance(all_matches[0], tuple):
            for match in all_matches:
                for column_name, value in zip(self.output_cols, match):
                    value = value.strip()
                    for clean_tag in self.parser_cleanup_tags:
                        value = value.replace(clean_tag, "")
                    sample[column_name].append(value)
        return sample
            
class SimpleLLMBlock(BaseLLMBlock, SimpleInputParse, SimpleOutParse):
    def __init__(self, **kwargs):
        BaseLLMBlock.__init__(self)
        SimpleInputParse.__init__(self, **kwargs)
        SimpleOutParse.__init__(self, **kwargs)

class LLMBlocWithCustomOutParse(BaseLLMBlock, SimpleInputParse, CustomOutParse):
    def __init__(self, **kwargs):
        BaseLLMBlock.__init__(self)
        SimpleInputParse.__init__(self, **kwargs)
        CustomOutParse.__init__(self, **kwargs)


if __name__ == "__main__":
    import prompt_templates as pts
    duplicate = DuplicateColumns()
    detailed_summary = SimpleLLMBlock(
        prompt_template=pts.detailed_summary,
        output_cols = ["summary_detailed"],
    )
    atomic_facts = SimpleLLMBlock(
        prompt_template=pts.atomic_facts,
        output_cols = ["summary_atomic_facts"]
    )
    
    extractive_summary = SimpleLLMBlock(
        prompt_template=pts.extractive_summary,
        output_cols = ["summary_extractive"]
    )

    generate_questions_and_responses = LLMBlocWithCustomOutParse(
        prep_fn = lambda sample: {'document': 
                                  (f"{sample['summary_detailed']}\n"
                                  f"{sample['summary_atomic_facts']}\n"
                                  f"{sample['summary_extractive']}\n"
                                  f"{sample['base_document']}"),
                                  "raw_document": sample.pop('document'),
                                  **sample},
        prompt_template=pts.generate_questions_and_responses,
        output_cols = ["question", "response"],
        parsing_pattern="\\[(?:Question|QUESTION)\\]\\s*(.*?)\\s*\\[(?:Answer|ANSWER)\\]\\s*(.*?)\\s*(?=\\[(?:Question|QUESTION)\\]|$)",
        parser_cleanup_tags=["[END]",]
    )
    
    duplicate >> detailed_summary
    detailed_summary >> atomic_facts
    atomic_facts >> extractive_summary
    extractive_summary >> generate_questions_and_responses
    flow = AsyncFlow(start=duplicate)

    from datasets import load_dataset
    data = load_dataset("json", data_files="/Users/aldo/Library/CloudStorage/GoogleDrive-aldito1@gmail.com/Other computers/My Mac/Projects/SDG-Research/examples/sdg_demo_output/seed_data.jsonl", split="train")
    sample = data[0]
    r = asyncio.run(flow.run_async(sample))
    # print(sample['summary_atomic_facts'])
    # r = asyncio.run(async_call_llm("hi"))


    from IPython import embed; embed()