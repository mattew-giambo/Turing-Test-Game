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




L'utente clicca avvia partita e dopo un ruolo. Invia una richiesta post al frontend dove dice sono player_name e voglio giocare come player_role
il frontend, fa una richiesta post al backend all'url start-game. Il backend avvia la partita e invia il game id al frontend. Quest'ultimo
rindirizza il client a localhost:port/game/id, il client quindi fa una richiesta get al frontend a questa pagina. Il frontend chiede informazioni
al backend riguardo al tipo di interfaccia che deve far vedere, quindi o del giudice o del partecipante. Il backend gli risponde con il
player role dell'utente e quindi il frontend capisce quale pagina fargli visualizzare.
Quando il player gioca come giudice avrà un form dove deve inserire tre domande, quando invia il form fa una richiesta post al frontend
che ed inoltra le domande al backend. Questo deciderà poi se far rispondere al database di sessioni vecchie oppure all'ai, restituisce 
le varie risposte al frontend.

Se il player gioca come partecipante farà una richiesta sulle domande a cui dovra rispondere sempre tramite form.
 
 

 

