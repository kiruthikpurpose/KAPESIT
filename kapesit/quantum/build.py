import os
import subprocess
import shutil

def build_cpp():
    cpp_dir = os.path.join(os.path.dirname(__file__), 'cpp')
    if os.path.exists(os.path.join(cpp_dir, 'build')):
        shutil.rmtree(os.path.join(cpp_dir, 'build'))
    
    os.makedirs(os.path.join(cpp_dir, 'build'))
    os.chdir(os.path.join(cpp_dir, 'build'))
    subprocess.run(['cmake', '..'])
    subprocess.run(['make'])

def build_java():
    java_dir = os.path.join(os.path.dirname(__file__), 'java')
    subprocess.run(['javac', '*.java'], cwd=java_dir)

def build_go():
    go_dir = os.path.join(os.path.dirname(__file__), 'go')
    subprocess.run(['go', 'build', '-o', 'quantum_go'], cwd=go_dir)

def build_csharp():
    csharp_dir = os.path.join(os.path.dirname(__file__), 'csharp')
    subprocess.run(['dotnet', 'build'], cwd=csharp_dir)

def build_asm():
    asm_dir = os.path.join(os.path.dirname(__file__), 'asm')
    for asm_file in os.listdir(asm_dir):
        if asm_file.endswith('.asm'):
            subprocess.run(['nasm', '-f', 'elf64', asm_file], cwd=asm_dir)

def clean():
    for lang in ['cpp', 'java', 'go', 'csharp', 'asm']:
        lang_dir = os.path.join(os.path.dirname(__file__), lang)
        if os.path.exists(lang_dir):
            for item in os.listdir(lang_dir):
                if item.endswith(('.o', '.exe', '.so', '.dll', '.class')):
                    os.remove(os.path.join(lang_dir, item))

def main():
    clean()
    build_cpp()
    build_java()
    build_go()
    build_csharp()
    build_asm()

if __name__ == '__main__':
    main()
