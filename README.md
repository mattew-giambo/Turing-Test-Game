# Idee

### Backend (API Server)
#### Endpoints:
- Login / Register: salva in un dizionario la sessione attiva  
- Avvia partita: salva in un dizionario la partita startata  
  Input:
  * Nome utente
  * Ruolo
- Partita del giudice: vengono prese le domande del giudice, viene estratto o AI o sessione vecchie, nel caso di sessioni vecchie vengono fuzzate le domande e nel caso ci fossero risposte adeguate vengono usate sessioni vecchie altrimenti AI.
- Viene aggiornato il dizionario con l'avversario corrispondente.   
  Input:
  * Id partita
  * Le 3 domande da porre
 
- Risposta del giudice: verifica se la risposta del giudice è corretta o meno andando a verificare il dizionario delle partite.
  Input:
  * risposta giudice
  * id partita
 
  - Partita del partecipante: viene scelto se deve rispondere a delle domande vecchie oppure generate da AI e vengono date le domande.
 
  - Risposte partecipante: vengono ricevute le risposte, vengono salvate nel dizionario e viene chiesto alla macchina se le risposte alle domande sono di un umano o meno. In base alla risposta viene assegnato un punteggio.

  - Get classifica punteggi
 
  - Get statistiche per utente divisa per ruolo (es quante partite vinte da giudice, quante vinte da partecipante)
 
### Frontend
#### Pagine html:
- Home dove viene spiegato il gioco
- Sezione di login e registrazione
- Dentro la dashboard, è presente un pulsante avvia partita e un pulsate profilo.
- Avviando la partita porta su un'altra pagina dove si seleziona o giudice o partecipante.
- Pagina di inserimento delle domande del giudice
- Pagina di inseriemto delle risposte dell'utente
- Pagina di caricamento
- pagina dei risultati

### Database
#### Users (id, nickname, email, hashed_password)
#### Stats (user_id, n_games, score_part, score_judge, won_part, won_judge, lost_part, lost_judge)
#### Games (id, user_id, player_role, result)
#### Q_A (game_id, question_id, question, answer, ai_question: bool, ai_answer: bool)
 
 

 

