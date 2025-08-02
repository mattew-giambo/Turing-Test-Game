questions_fuzzy = [
    {"Cosa ti piace mangiare?":[
        {
        "question": "Cosa ti piace fare?",
        "answer": "la spesa"
    }]},
    {"Ciao afafafff?": [{
        "question": "Cosa ti piace fare?",
        "answer": "la spesa"
    }, {
        "question": "Cosa ti piace fare?",
        "answer": "la spesa"
    }, {
        "question": "Cosa ti piace fare?",
        "answer": "la spesa"
    }, {
        "question": "Cosa ti piace fare?",
        "answer": "la spesa"
    }]
}]

for q_fuzzy in questions_fuzzy:
    question_input = list(q_fuzzy.keys())[0] # question_input è l'unica chiave
    lista_domande_risposta = q_fuzzy[question_input]

    prompt = (
                "Ti darò una domanda e una lista di risposte. "
                "Scegli la risposta migliore per la domanda fornita.\n"
                "Rispondi solo con il numero corrispondente (ad esempio '1').\n\n"
                f"Domanda: {question_input}\n"
            ) 
    for idx, qa in enumerate(lista_domande_risposta, start= 1):
        prompt+=f"{idx}. {qa['answer']}\n"
    print(prompt)