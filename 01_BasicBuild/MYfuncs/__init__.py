# For relative imports to work in Python 3.6+
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))



from pathlib import Path
print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())


if __name__ == "__main__":
    main()