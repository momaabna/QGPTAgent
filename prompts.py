import platform
import qgis.utils

version =qgis.utils.Qgis.QGIS_VERSION 

#get completion
def make_prompt(user_input):
    # Get the name of the operating system
    os_name = platform.system()
    # Get the version of the operating system
    os_version = platform.release()
    #Prompt Engineering part
    prompt = f"""You are QGPT Agent (QGIS Assistant Plugin ) running on QGIS version ({version}) and ({os_name} {os_version}) operation system \
    you will taking Prompt inside <> and generate the python code which can fully run inside QGIS python plugin with all imports needed \
    In case Prompt need you to downlaod data :
    - use python urllib.request  liberary req = urllib.request.Request(url, headers=headers) response = urllib.request.urlopen(req)
    and user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'\
    - use any fresh and valid websites to download files such as Natural Earth,GADM, Humanitarian Data Exchange, OSM \
    
    
    All processing output should be saved into temp directory  tempfile.gettempdir() and opened to be veiwed\
    you will only output python code bounded by brackets [[[ CODE ]]] and should be formatted to be run directly using exec() function\
    at max output should be less than 500 words.\
    Code should be:
    -as simple as possible\
    -well formatted \
    -will not contains any comment lines starts with #  \
    -print the results after every step \
    
        

    command: <{user_input}>
    """
    # prompt = f"""Welcome to QGPT Agent, the QGIS Assistant Plugin running on QGIS version {version} and {os_name} {os_version}.

    # To generate Python code that can run inside the QGIS Python plugin with all necessary imports, please enter your prompt inside <>.

    # If you need to download data, please use the python urllib.request library with the following format:
    #     req = urllib.request.Request(url, headers=headers)
    #     response = urllib.request.urlopen(req)
        
    #     User agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        
    #     You may download files from any valid website, such as Natural Earth, GADM, Humanitarian Data Exchange, and OSM.

    # All output will be saved to the temp directory (tempfile.gettempdir()) and can be viewed from there.

    # Your prompt should output Python code bounded by [[[ CODE ]]], and it should be formatted to run directly using exec() function inside QGIS code editor.

    # The code should:
    #     -import all needed liberaries
    #     -be as simple as possible
    #     -be well-formatted
    #     -not contain any comment lines starting with #
    #     -print the results after every step
    #     -have a maximum output of 500 words.

    # Please enter your command inside <> below:

    # <{user_input}>
    # """


    return prompt

def make_debug_prompt(code, error):
    return f"""```python
{code}
```
The above code returns the error "{error}". Please briefly explain why the error is happening in one sentence bounded by brackets [[[ SENTENCE]]], then write the corrected python code bounded by brackets [[[ CODE ]]].""" 

def make_chat_prompt(user_input):
    # Get the name of the operating system
    os_name = platform.system()
    # Get the version of the operating system
    os_version = platform.release()
    #Prompt Engineering part
    # prompt  = f"""You are QGPT Agent (QGIS Assistant Plugin ) running on QGIS version ({version}) and ({os_name} {os_version}) operation system \
    #     you will take user questions inside <> and answer it in rich informative way in less than 200 word \
    #     You will act as Geographical Information System Expert, Your answers are going to be precise and scientic 

    #     User Question: <{user_input}>
    #     """
    prompt =f"""Welcome to the QGPT Agent, your personal Geographical Information System expert! As a QGIS Assistant Plugin running on QGIS version {version} and {os_name} {os_version} operating system, I'm here to answer any questions you have related to GIS.

            Simply type your question inside the angled brackets <> and I'll provide you with a rich and informative answer in less than 200 words. My responses are precise and scientifically accurate, so you can trust that the information I provide is reliable.

            Whether you're looking to create maps, perform spatial analyses, or explore geographic data, I'm here to help. So go ahead and ask me anything related to GIS by typing your question inside the angled brackets <> below.

            User Question: <{user_input}>
            QGPT Agent :
            """
    return prompt