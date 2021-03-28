import sys, os, os.path, glob
from code_writer import CodeWriter
from parser import Parser

from vm_constant import *
import argparse
import glob



def main(infile_path: str, outfile_path: str):
    print(infile_path)
    vm_files = [path for path in glob.glob(infile_path +"/*.vm")]
    code_writer = CodeWriter(filepath=outfile_path)
    code_writer.write_init()
    for filepath in vm_files:
        print(filepath)
        parser = Parser(filepath=filepath)
        code_writer.set_file_path(filepath)
        while parser.hasMoreCommands():
            cmd = parser.commandType()
            if cmd == C_ARITHMETIC:
                code_writer.writeArithmetic(parser.arithmetic())
            elif cmd == C_PUSH or cmd == C_POP:
                code_writer.writePushPop(cmd, parser.arg1(), index=int(parser.arg2()))
            elif cmd == C_LABEL:
                code_writer.writeLabel(parser.arg1())
            elif cmd == C_GOTO:
                code_writer.writeGoto(parser.arg1())
            elif cmd == C_IF:
                code_writer.writeIf(parser.arg1())
            elif cmd == C_FUNCTION:
                code_writer.writeFunction(parser.arg1(), parser.arg2())
            elif cmd == C_RETURN:
                code_writer.writeReturn()
            elif cmd == C_CALL:
                code_writer.writeCall(parser.arg1(), parser.arg2())
            parser.advance()
    code_writer.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='For Assembler')
    parser.add_argument("infile_dir_path", type=str, default=None)
    parser.add_argument("outfile_path", type=str, default=None)
    args = parser.parse_args()

    main(args.infile_dir_path, args.outfile_path)