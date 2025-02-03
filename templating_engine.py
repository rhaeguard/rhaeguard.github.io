import re
import enum

class BlockType(enum.Enum):
    RAW_STRING = 0
    EXPRESSION = 1
    FUNCTION_CALL = 2

class FunctionCallBlock:

    def __init__(self, function_name: str, params: list[str], body: list['Block']):
        self.function_name = function_name
        self.params = params
        self.body = body

class Block:
    def __init__(self, type: BlockType, value):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"{str(self.type)}"
    
    def render(self, context):
        if self.type == BlockType.RAW_STRING:
            context["__out__"] += str(self.value)
        elif self.type == BlockType.EXPRESSION:
            try:
                result = eval(self.value, context)
                context["__out__"] += str(result)
            except Exception as e:
                print(f"expression '{self.value}' resulted in an error", str(e))

        elif self.type == BlockType.FUNCTION_CALL:
            fb: FunctionCallBlock = self.value
            invoke(fb, context)
        else:
            raise Exception(f"unsupported type: {str(self.type)}")

def func_for(context: dict, params: list[str], body: list['Block']):
    assert len(params) == 2, "for function accepts 2 params: [varname, iterable]"
    varname, itername = params
    iterable = context[itername]

    for value in iterable:
        context[varname] = value
        
        for block in body:
            block.render(context)

        del context[varname]

def func_if(context: dict, params: list[str], body: list['Block']):
    assert len(params) == 1, "if function accepts 1 param: [condition]"
    
    condition_expression = params[0]
    
    try:
        result = bool(eval(condition_expression, context))
    except NameError:
        result = False

    if result:
        for block in body:
            block.render(context)
    context["__if_result__"] = result

def func_switch(context: dict, params: list[str], body: list['Block']):
    assert len(params) == 0, "switch function accepts 0 param: []"
    components: list['Block'] = []
    default_branch = None
    for b in body:
        if b.type == BlockType.FUNCTION_CALL:
            func: FunctionCallBlock = b.value
            if func.function_name == "default":
                if default_branch is not None:
                    raise Exception("switch function only allows one 'default' expression")
                default_branch = b
            elif func.function_name == "when":
                components.append(b)
            else:
                raise Exception("switch function only allows 'when' and 'default' expressions")

    for c in components:
        c.render(context)
        
        if context["__if_result__"] == True:
            default_branch = None
        
        context.pop("__if_result__", None)

    if default_branch:
        default_branch.render(context)


def func_default(context: dict, params: list[str], body: list['Block']):
    assert len(params) == 0, "default function accepts 0 param: []"

    for b in body:
        b.render(context)

def func_format_date(context: dict, params: list[str], body: list['Block']):
    MARKDOWN_ARTICLE_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
    assert len(params) == 1, "format_date function accepts 1 param: [date_str]"

    from datetime import datetime

    date_str = params[0]
    date_str = eval(date_str, context) 
    date = datetime.strptime(date_str, MARKDOWN_ARTICLE_DATE_FORMAT).date()

    context["__out__"] += str(date)

FUNCTION_MAP = {
    "for": func_for,
    "when": func_if,
    "switch": func_switch,
    "default": func_default,
    "format_date": func_format_date,
}

def invoke(fb: 'FunctionCallBlock', context: dict):
    FUNCTION_MAP[fb.function_name](context, fb.params, fb.body)


def parse_block(tokens, i):
    i += 1
    current_template: list[Block] = []
    while i < len(tokens):
        token = tokens[i]
        if token == "{{":
            x, template = parse_block(tokens, i)
            i = x
            current_template.append(template)
        elif token == "}}":
            if "(" not in current_template[0].value:
                blockType = BlockType.EXPRESSION
                value = current_template[0].value
            else:
                blockType = BlockType.FUNCTION_CALL

                # the way a function call is structured is as follows:
                # function(params) <body>
                first = current_template[0]
                body = current_template[1:]

                assert first.type == BlockType.RAW_STRING, "the first parameter of expression is not of supported type"
                
                rparen = first.value.find(")")
                lparen = first.value.find("(")
                assert rparen != -1 and lparen != -1, f"invalid function call format: {first.value}"
                
                function_name = first.value[:lparen]
                function_params = list(filter(bool, map(str.strip, first.value[lparen+1:rparen].split(","))))

                remainder = first.value[rparen+1:]
                body = [Block(BlockType.RAW_STRING, remainder)] + body

                value = FunctionCallBlock(function_name, function_params, body)
            t = Block(blockType, value)
            return i, t
        else:
            t = Block(BlockType.RAW_STRING, token)
            current_template.append(t)
        i += 1
    raise Exception("syntax error")

def parse(tokens: list[str], i = 0):
    blocks: list[Block] = []
    while i < len(tokens):
        token = tokens[i]

        if token == "{{":
            x, template = parse_block(tokens, i)
            i = x
            blocks.append(template)
        else:
            blocks.append(Block(BlockType.RAW_STRING, token))

        i += 1
    return blocks

def do_render_template(text: str, context) -> str:
    pieces = re.split(r'({{|}})', text)
    result = parse(pieces)
    context = {
        "__out__": "",
        "date": "2028-10-10",
        "title": "my title yay!",
        "counts": list(range(15)),
        "content": {
            "hallo": {
                "hi": "this will be epic"
            }
        },
        "github": "rhaeguard/rgx",
        "age": 30
    }
    for p in result:
        p.render(context)

    return context["__out__"]

def render_template(text: str, context: dict) -> str:
    pieces = re.split(r'({{|}})', text)
    result = parse(pieces)

    context["__out__"] = ""

    for p in result:
        p.render(context)

    return context["__out__"]


if __name__ == "__main__":
    with open ("./templates/t.template.html", encoding="utf-8") as tf:
        contents = tf.read()
       
    print(do_render_template(contents))
