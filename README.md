# POLAR.AI: A project for a locally hosted LLM

POLAR.AI is an open-source project accesible for everyone. This is meant to be a personal project to learn how to train a foundational model in different ways such as fine-tunning and LLM Inference among others.

There will be a website app developed in flask that will ensure the user every aspect of the training and ussage phase, meaning that the final product is meant to be fully used by the app and not by python scripts.

>**WARNING**
>the file `server/data/config.json` is missing, it is needed to specify the Port in which the app will be accesed, also the IP of the hosting server:
>```json
>{
>   "PORT": "custom_port",
>   "IP": "custom_ip"
>}
>```

to start running the app execute in the terminal:
```shell
source venv/bin/activate
python3 server/main.py
```
you should get an output similar to this:
```shell
 * Serving Flask app 'main'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://[IP]:[PORT]
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: [PIN]
```