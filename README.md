# bulgakov-cache-script

### Downloading material from your lessons from LXP IThub.

# Before using

Step 1: Installing dependencies.

```sh
pip3 install -r requirements.txt
```

Step 2: Provide of your login data in input.json.

```json
{
  // Example of input.json
  "login": " Yourlogin@mail.com",
  "password": "password"
}
```

# Example of using

```sh
# To download a certain discipline (take the discipline id from the address bar)
./main.py -m md -c input.json --subject 1234

# To download all disciplines
./main.py -m md -c input.json

# Show all use cases
./main.py -h
```

# Maintainers

[Igor Molchanov](https://github.com/meg4cyberc4t)

This library is open for issues and pull requests. If you have ideas for improvements or bugs, the repository is open to contributions!

# License

[GNU GENERAL PUBLIC LICENSE](LICENSE)
