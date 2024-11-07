import google.generativeai as genai   

def gera_prompt(template, temperatura, umidade, co2):
    genai.configure(api_key="AIzaSyChtbxglA_gwNop0FmeUrirEwxrE71dQXQ")

    try:
        generative_model = genai.GenerativeModel('gemini-1.5-flash')
        response = generative_model.generate_content(
            f"neste template a seguir troque o a temperatura por {temperatura} e a umidade por {umidade}: {template} sem Explicação do código e sem comentar quais foram as alterações"
            #f"Monte um corpo de e-mail html/css para informar os seguintes valores de dados, temperatura de {temperatura}, umidade de {umidade}, altitude de {altitude}, pressao de {pressao} e co2 de {co2} sem Explicação do código"
        )

        # Verificar se a resposta tem um campo 'content' ou 'text'
        if hasattr(response, 'content'):
            resposta = response.content
        elif hasattr(response, 'text'):
            resposta = response.text
        else:
            resposta = "Erro ao obter a resposta da API"
        
        print("Resposta da API Gemini:", resposta)
        return resposta

    except Exception as e:
        print(f"Erro ao chamar a API Gemini: {str(e)}")
        return "Erro ao obter a resposta da API"