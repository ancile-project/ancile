from ancile.core.core import execute

def main():
    with open('program.py') as f:
        program = f.read()

    execute(program=program,
            users_secrets=[],
            data_policy_pairs=[],
            app_module=None,
            app_id=None)

if __name__ == "__main__":
    main()
