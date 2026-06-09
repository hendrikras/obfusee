import sys
import importlib


def main():
    args = sys.argv[1:]

    # Determine mode: -e for encode, -d for decode
    has_encode = "-e" in args
    has_decode = "-d" in args

    if has_encode and has_decode:
        print("Error: specify either -e (encode) or -d (decode), not both.")
        sys.exit(1)

    if has_encode:
        mode = "encode"
        flag = "-e"
    elif has_decode:
        mode = "decode"
        flag = "-d"
    else:
        print("Usage: python main.py -e <document> <input_csv> [-b]")
        print("       python main.py -d <document> <encoded_file> [-b]")
        sys.exit(1)

    # Remove the flag from args, forward everything else
    flag_idx = args.index(flag)
    forward_args = args[:flag_idx] + args[flag_idx + 1:]

    # Reconstruct sys.argv for the sub-module
    old_argv = sys.argv
    sys.argv = [f"obfusee_{mode}.py"] + forward_args

    try:
        module = importlib.import_module(mode)
        module.main()
    finally:
        sys.argv = old_argv


if __name__ == "__main__":
    main()
