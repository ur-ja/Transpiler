#!/usr/bin/python3 -u
import sys, re

python_code = [] 

def get_indentation(line):
    return len(line) - len(line.lstrip())

def comment(line):
    inline = re.search(r'.+(#.*)', line)
    if inline:
        python_code.append(inline.group(1))
    else:
        python_code.append(line) 

def variable(line):
    text = line.strip()
    num_args = re.search(r'.*\s*\$#\s*.*', text)
    all_args = re.search(r'.*\s*\$@\s*.*', text)
    is_single_quotes = re.search(r".*'.*\$.*'.*", text)
    brace = re.search(r".*\${.*}.*", text)
    is_double_quotes = re.search(r'.*".*\$.*".*', text)
    argument = re.search(r"\$(\d)(?=(?:[^']*'[^']*')*[^']*$)", text)
    is_backticks = re.search(r'.*`(.*)`.*', line.strip())

    if is_backticks:
        text = backticks(text)
    if is_single_quotes:
        text = re.sub(r"}", r"}}", re.sub(r"{", r"{{", text))
        text = single_quotes(text)
        return text
    if all_args:
        handle_import('import sys')
        text = re.sub(r'\$@', r'{" ".join(sys.argv[1:])}', text)
        return text
    if is_double_quotes:
        text = double_quotes(text)
    if num_args:
        handle_import('import sys')
        text = re.sub(r'\$#', r'{len(sys.argv) - 1}', text)
        return text
    if argument:
        handle_import('import sys')
        text = re.sub(r'\$(\w+)', r'{sys.argv[\1]}', text)
    if brace:
        text = re.sub(r'\$({\w+})', r'\1', text)
    text = re.sub(r'\$(\w+)', r'{\1}', text)
    return text

def globbing(line):
    text = line.strip()
    is_single_quotes = re.search(r"'.*[\*|?|\[|\]].*'", text)
    is_double_quotes = re.search(r'".*[\*|?|\[|\]].*"', text)
    is_variable = re.search(r'.*$.*', text)

    if is_variable:
        text = variable(text)

    if is_single_quotes:
        return single_quotes(text)
    
    if is_double_quotes:
        return double_quotes(text)
        
    handle_import('import glob')
    text = re.sub(r'([\*|?|\[|\]]\S+)', r'{" ".join(sorted(glob.glob(f"\1")))}', text)
    return text

def single_quotes(line):
    text = line.strip()
    single_quoted_strings = re.findall(r"'.*?'", text)
    for s in single_quoted_strings:
        unquoted_content = s[1:-1]  # Remove the single quotes from the string
        text = text.replace(s, unquoted_content)
    return text

def double_quotes(line):
    return re.sub(r'"(.*)"', r"\1", line.strip())
    
def echo(line):
    is_inline_comment = re.search(r'echo(.+)(\s+)(#.*)', line.strip())
    is_variable = re.search(r'echo(.*)(\$.*)(.*)', line.strip())
    is_globbing = re.search(r' ([*?[\]])', line.strip())
    n_flag = re.search(r'echo(\s+)-n(\s+)(.*)', line)
    is_backticks = re.search(r'.*`(.*)`.*', line.strip())
    text = line.strip()

    if is_backticks:
        text = backticks(text)
    if is_variable:
        text = variable(text)
    if is_globbing:
       text = globbing(text)
    if is_inline_comment:
        text = re.search(r'echo\s+(.+[^\s])(\s+)(#.*)', text)
        python_code.append(' ' * get_indentation(line) + f"print(f'{text.group(1)}'){text.group(2)}{text.group(3)}")
        return

    text = re.search(r'echo\s*(.*)', text)
    text = ' '.join(text.group(1).strip().split())

    is_single_quotes = re.search(r".*'(.*)'.*", line)
    is_double_quotes = re.search(r'.*"(.*)".*', line)
    if is_single_quotes:
        text = re.sub(r"'(.*)'", rf'{is_single_quotes.group(1)}', text)
        text = re.sub(r'"', r'\\"', text)
        text = single_quotes(text)
    elif is_double_quotes:
        text = re.sub(r'"(.*)"', rf'{is_double_quotes.group(1)}', text)
        text = re.sub(r"'", r"\\'", text)
        text = double_quotes(text)
        if is_backticks: text = backticks(text)

    if n_flag:
        text = re.sub(r'\s*-n', r'', text)
        python_code.append(' ' * get_indentation(line) + f"print(f'{text}', end='')")
    else:
        python_code.append(' ' * get_indentation(line) + f"print(f'{text}')")


def assignment(line):
    is_variable = re.search(r'.*\$.*', line.strip())
    is_globbing = re.search(r'([*?[\]])', line.strip())
    is_inline_comment = re.search(r'(.+)=(.*[^\s])(\s+)(#.*)', line.strip())
    is_single_quotes = re.search(r".*'(.*)'.*", line.strip())
    is_double_quotes = re.search(r'.*"(.*)".*', line.strip())
    is_backticks = re.search(r'.*`(.*)`.*', line.strip())

    text = line.strip()
    if is_variable:
        text = variable(text)
    if is_single_quotes:
        text = single_quotes(text)
    if is_double_quotes:
        text = double_quotes(text)
    if is_globbing:
       text = globbing(text)
    if is_inline_comment:
        text = re.search(r'(.+)=(.*[^\s])(\s+)(#.*)', line)
        python_code.append(' ' * get_indentation(line) + f"{text.group(1)} = f'{text.group(2)}'{text.group(3)}{text.group(4)}")
        return
    if is_backticks:
        text = backticks(text)
        text = re.sub(r'[{}]', r'', text)
        text = re.search(r'(.*)=(.*)', text)
        python_code.append(' ' * get_indentation(line) + f"{text.group(1)} = {text.group(2)}")
        return

    text = re.search(r'(.*)=(.*)', text)
    python_code.append(' ' * get_indentation(line) + f"{text.group(1)} = f'{text.group(2)}'")

def backticks(line):
    is_backticks = re.search(r'.*`(.*)`.*', line.strip())
    if not is_backticks:
        return line
    content = subprocess(is_backticks.group(1), False)
    text = re.sub(r'`.*`', f'{{{content}}}', line)
    pattern = r'subprocess.run\((\[.*\])\)'
    replacement = 'subprocess.run(\\1, capture_output=True, text=True).stdout.strip()'
    text = re.sub(pattern, replacement, text)
    return text

def loop(line):
    is_globbing = re.search(r'([*?[\]])', line)
    is_variable = re.search(r'.*\$.*', line)
    is_backticks = re.search(r'.*`(.*)`.*', line.strip())
    text = line.strip()

    if is_backticks:
        text = backticks(text)
    if is_variable:
        text = variable(text)
    if is_globbing:
        text = globbing(line)
        text = re.sub(r'" ".join\((sorted\(.*\))\)', r'\1', text)
        text = re.sub(r'{(.*)}', r'\1', text)
    else:
        array = re.findall(r'\w+', re.search(r'for \w+ in (.*)', text).group(1))
        text = re.sub(r'in (.*)', rf'in {array}', text)

    text = text.strip() + ':'
    python_code.append(' ' * get_indentation(line) + text)
        
def exit(line):
    is_number = re.search(r'exit (\d+)', line)
    text = line.strip()

    handle_import('import sys')

    if is_number:
        text = re.sub(r'exit (\d+)', r'sys.exit(\1)', text)
    else:
        text = re.sub(r'exit', r'sys.exit()', text)
    
    python_code.append(' ' * get_indentation(line) + f'{text.strip()}\n')

def cd(line):
    is_variable = re.search(r'.*\$.*', line)
    text = line.strip()
    handle_import('import os')
    if is_variable:
        text = variable(text)
    text = re.sub(r'cd ([\S]+)', r'os.chdir("\1")', text)
    python_code.append(' ' * get_indentation(line) + text)

def read(line):
    text = re.sub(r'read ([\S]+)', r'\1 =  input()', line.strip())
    python_code.append(' ' * get_indentation(line) + text)

def handle_import(module):
    if module not in python_code:
        python_code.insert(1, module)

def subprocess(line, output):
    is_inline_comment = re.search(r'.*(#.*)', line)
    is_globbing = re.search(r'([*?[\]])', line.strip())
    is_variable = re.search(r'.*$.*', line.strip())

    if is_variable:
        text = variable(line)

    words = re.findall(r'\S+', text)
    command = words[0]
    args_str = f"subprocess.run(['{command}', "
    handle_import('import subprocess')

    for word in words[1:]:
        if re.search(r'".*"', word):
            word = double_quotes(word)
        if word.startswith('#'):
            break
        if word.startswith('$'):
            args_str += word[1:] + ', '
        if re.search(r'([*?[\]])', word):
            handle_import('import glob')
            word = re.sub(r'([\*|?|\[|\]]\S+)', r'glob.glob("\1")', word)
            args_str = args_str[:-2]
            args_str += '] + ' + word + ')'
        else:
            args_str += f"'{word}', "

    if not is_globbing:
        args_str = args_str.rstrip(', ') + '])'

    if is_inline_comment:
        args_str = args_str.strip() + ' ' + is_inline_comment.group(1)

    if output:
        python_code.append(' ' * get_indentation(line) + args_str)
    else:
        return args_str
    
def test1(line):
    string_equals = re.search(r'test (.*[^!])=(.*)', line)
    string_not_equals = re.search(r'test (.*)!=(.*)', line)
    not_equals = re.search(r'test (.*)-ne(.*)', line)
    equals = re.search(r'test (.*)-eq(.*)', line)
    greater = re.search(r'test (.*)-gt(.*)', line)
    less = re.search(r'test (.*)-lt(.*)', line)

    text = line
    
    if string_equals:
        text = re.sub(r'test (.*[^!\s])(\s+)=(\s+)(\S+)', r'f"\1" == f"\4":', text)
    elif string_not_equals:
        text = re.sub(r'test (.*[^!\s])(\s+)!=(\s+)(\S+)', r'f"\1" != f"\4":', text)
    elif not_equals:
        text = re.sub(r'[{}]', r'', text)
        text = re.sub(r'test (.*[^!\s])(\s+)-ne(\s+)(\S+)', r'\1 != \4:', text)
    elif equals:
        text = re.sub(r'[{}]', r'', text)
        text = re.sub(r'test (.*[^!\s])(\s+)-eq(\s+)(\S+)', r'\1 == \4:', text)
    elif greater:
        text = re.sub(r'[{}]', r'', text)
        text = re.sub(r'test (.*[^!\s])(\s+)-gt(\s+)(\S+)', r'\1 > \4:', text)
    elif less:
        text = re.sub(r'[{}]', r'', text)
        text = re.sub(r'test (.*[^!\s])(\s+)-lt(\s+)(\S+)', r'\1 < \4:', text)
    return text

def test2(line):
    greater_or_equals = re.search(r'test (.*)-ge(.*)', line)
    less_or_equals = re.search(r'test (.*)-le(.*)', line)
    access_flags = re.search(r'test\s+-([rfwx])\s+(.*)', line)
    and_flag = re.search(r'test(.*[^!\s])(\s+)-a(\s+)(.*)', line)
    or_flag = re.search(r'test(.*[^!\s])(\s+)-o(\s+)(.*)', line)
    d_flag = re.search(r'test\s+-d\s+(.*)', line)
    

    text = line
    if greater_or_equals:
        text = re.sub(r'[{}]', r'', text)
        text = re.sub(r'test (.*[^!\s])(\s+)-ge(\s+)(\S+)', r'\1 >= \4:', text)
    elif less_or_equals:
        text = re.sub(r'[{}]', r'', text)
        text = re.sub(r'test (.*[^!\s])(\s+)-le(\s+)(\S+)', r'\1 <= \4:', text)
    elif and_flag:
        text = re.sub(r'test(.*[^!\s])(\s+)-a(\s+)(\S+)', r'f"\1" and f"\4":', text)
    elif or_flag:
        text = re.sub(r'test(.*[^!\s])(\s+)-o(\s+)(\S+)', r'f"\1" or f"\4":', text)
    elif access_flags:
        handle_import('import os')
        flag = access_flags.group(1).upper()
        access_flags = re.search(r'test\s+-([rfwx])\s+(.*)', text)
        text = re.sub(r'test\s+-([rfwx])\s+(\S+)', rf'os.access(f"{access_flags.group(2)}", os.{flag}_OK):', text)
    elif d_flag:
        handle_import('import os')
        text = re.sub(r'test\s+-d\s+(\S+)', r'os.path.isdir(f"\1"):', text)
    return text

def test3(line):
    c_flag = re.search(r'test(\s+)-c(\s+)(.*)', line)
    z_flag = re.search(r'test(\s+)-z(\s+)(.*)', line)
    e_flag = re.search(r'test(\s+)-e(\s+)(.*)', line)
    g_flag = re.search(r'test(\s+)-g(\s+)(.*)', line)
    p_flag = re.search(r'test(\s+)-p(\s+)(.*)', line)
    
    text = line
    if z_flag:
        text = re.sub(r'test\s+-z\s+(\S+)', r'! f"\1":', text)
    elif p_flag:
        handle_import('import os')
        handle_import('import stat')
        text = re.sub(r'test\s+-p\s+(\S+)', r'os.path.exists(f"\1") and stat.S_ISFIFO(os.stat(f"\1").st_mode):', text)
    elif g_flag:
        handle_import('import os')
        handle_import('import stat')
        text = re.sub(r'test\s+-g\s+(\S+)', r'os.path.exists(f"\1") and (os.stat(f"\1").st_mode & stat.S_ISGID):', text)
    
    elif c_flag:
        handle_import('import os')
        handle_import('import stat')
        text = re.sub(r'test\s+-c\s+(\S+)', r'os.path.exists(f"\1") and stat.S_ISCHR(os.stat(f"\1").st_mode):', text)
    elif e_flag:
        handle_import('import os')
        text = re.sub(r'test\s+-e\s+(\S+)', r'os.path.exists(f"\1"):', text)
    return text


def test4(line):
    h_or_upper_l_flag = re.search(r'test(\s+)-[hL](\s+)(.*)', line)
    k_flag = re.search(r'test(\s+)-k(\s+)(.*)', line)
    nt_flag = re.search(r'test(\s+)(.*)(\s+)-nt(\s+)(.*)', line)
    ot_flag = re.search(r'test(\s+)(.*)(\s+)-ot(\s+)(.*)', line)
    n_flag = re.search(r'test(\s+)-n(\s+)(.*)', line)
    b_flag = re.search(r'test(\s+)-b(\s+)(.*)', line)

    text = line
    
    if nt_flag:
        handle_import('import os')
        text = re.sub(r'test(\s+)(.*)(\s+)-nt(\s+)(\S+)', r'os.path.getmtime(f"\2") > os.path.getmtime(f"\5"):', text)
    elif ot_flag:
        handle_import('import os')
        text = re.sub(r'test(\s+)(.*)(\s+)-ot(\s+)(\S+)', r'os.path.getmtime(f"\2") < os.path.getmtime(f"\5"):', text)
    elif h_or_upper_l_flag:
        handle_import('import os')
        text = re.sub(r'test\s+-[hL]\s+(\S+)', r'os.path.exists(f"\1") and os.path.islink(f"\1")):', text)
    elif k_flag:
        handle_import('import os')
        handle_import('import stat')
        text = re.sub(r'test\s+-k\s+(\S+)', r'os.path.exists(f"\1") and (os.stat(f"\1").st_mode & stat.S_ISVTX):', text)
    elif n_flag:
        text = re.sub(r'test\s+-n\s+(\S+)', r'f"\1":', text)
    elif b_flag:
        handle_import('import os')
        handle_import('import stat')
        text = re.sub(r'test\s+-b\s+(\S+)', r'os.path.exists(f"\1") and stat.S_ISBLK(os.stat(f"\1").st_mode):', text)
    return text

def test5(line):
    upper_g_flag = re.search(r'test(\s+)-G(\s+)(.*)', line)
    upper_n_flag = re.search(r'test(\s+)-N(\s+)(.*)', line)
    upper_o_flag = re.search(r'test(\s+)-O(\s+)(.*)', line)
    s_flag = re.search(r'test(\s+)-s(\s+)(.*)', line)
    upper_s_flag = re.search(r'test(\s+)-S(\s+)(.*)', line)
    u_flag = re.search(r'test(\s+)-u(\s+)(.*)', line)

    text = line
    if s_flag:
        handle_import('import os')
        text = re.sub(r'test\s+-s\s+(\S+)', r'os.path.exists(f"\1") and os.path.getsize(f"\1") > 0:', text)
    elif upper_s_flag:
        handle_import('import os')
        handle_import('import stat')
        text = re.sub(r'test\s+-S\s+(\S+)', r'os.path.exists(f"\1") and stat.S_ISSOCK(os.stat(f"\1").st_mode):', text)
    elif u_flag:
        handle_import('import os')
        handle_import('import stat')
        text = re.sub(r'test\s+-u\s+(\S+)', r'os.path.exists(f"\1") and (os.stat(f"\1").st_mode & stat.S_ISUID):', text)
    elif upper_g_flag:
        handle_import('import os')
        text = re.sub(r'test\s+-G\s+(\S+)', r'os.path.exists(f"\1") and os.stat(f"\1").st_gid == os.getegid():', text)
    elif upper_o_flag:
        handle_import('import os')
        text = re.sub(r'test\s+-O\s+(\S+)', r'os.path.exists("\1") and os.stat("\1").st_uid == os.geteuid():', text)
    elif upper_n_flag:
        handle_import('import os')
        handle_import('import time')
        text = re.sub(r'test\s+-N\s+(\S+)', r'os.path.exists(f"\1") and time.time() - os.stat(f"\1").st_mtime > 0:', text)
    return text


def test(line):
    is_variable = re.search(r'test.*\$.*', line)
    is_double_quotes = re.search(r'.*".*".*', line)
    is_single_quotes = re.search(r".*'.*'.*", line)
    text = line.strip()

    if is_variable:
        text = variable(text)
    if is_double_quotes:
        text = double_quotes(text)
    if is_single_quotes:
        text = single_quotes(text)

    text = test1(text)
    text = test2(text)
    text = test3(text)
    text = test4(text)
    text = test5(text)

    if text == line.strip():
        text = re.sub(r'test(\S+)', r'\1:', text)

    python_code.append(' ' * get_indentation(line) + text)



def main():
    filename = sys.argv[1]

    with open(filename, 'r') as file:
        for line in file:
            if re.match(r'^#!/bin/dash$', line):
                python_code.append(' ' * get_indentation(line) + '#!/usr/bin/python3 -u')
            elif line.strip() == '':  
                python_code.append('')
            elif re.search(r'^\s*#(.*)', line):
                comment(line)
            elif re.search(r'echo.*', line):
                echo(line)
            elif re.search(r'test .*', line):
                test(line)
            elif re.search(r'(.+)=(.+)', line):
                assignment(line)
            elif re.search(r'for .*', line):
                loop(line)
            elif re.search(r'exit', line):
                exit(line)
            elif re.search(r'cd (.*)', line):
                cd(line)
            elif re.search(r'read (.*)', line):
                read(line)
            elif re.search(r'else', line.strip()):
                python_code.append(' ' * get_indentation(line) + line.strip() + ':')
            elif re.search(r'while true', line):
                python_code.append(' ' * get_indentation(line) + 'while True' + ':')
            elif re.search(r'\s*do', line.strip()) or re.search(r'\s*done', line.strip()) or re.search(r'\s*then', line.strip()) or re.search(r'\s*fi', line.strip()):
                is_inline_comment = re.search(r'.*(#.*)', line)
                if is_inline_comment:
                    text = is_inline_comment.group(1)
                else:
                    text = re.sub(r'[do|then|fi|done]', r'', line.strip())
                python_code.append(' ' * get_indentation(line) + text)
            else:
                subprocess(line, True)

    for code_line in python_code:
        print(code_line)

if __name__ == "__main__":
    main()


