import openenv
from environment import SOCEnv

def main():
    openenv.serve(SOCEnv)

if __name__ == "__main__":
    main()