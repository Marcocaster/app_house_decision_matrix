import pandas as pd
import streamlit as st
import requests
import io  # per gestire file in memoria

def main():
    # Inizializza lo stato della sessione per abilitare il modulo
    if "proceed" not in st.session_state:
        st.session_state.proceed = False

    # Schermata iniziale per il benvenuto e la richiesta del nome
    st.title("Benvenuto nella Decision Matrix")
    user_name = st.text_input("Inserisci il tuo nome (es. Teo):", "")

    if st.button("Inizia"):
        if user_name.strip() == "":
            st.error("Per favore, inserisci il tuo nome!")
        else:
            st.session_state.proceed = True
            st.session_state.user_name = user_name

    # Se l'utente ha cliccato "Inizia", mostra il modulo completo
    if st.session_state.proceed:
        st.title("Decision Matrix per la scelta della casa della nonna Manu e nipotazzi")
        st.subheader("Istruzioni: assegna un peso (1-10) a ciascun fattore e poi valuta le case.")

        # Personalizza i nomi delle case (i "fogli" che avranno casa loro)
        st.header("Personalizza i nomi delle case")
        casa_a_nome = st.text_input("Nome per Casa A (es. 'Casa Centro')", "Casa A")
        casa_b_nome = st.text_input("Nome per Casa B (es. 'Casa Villetta')", "Casa B")
        casa_c_nome = st.text_input("Nome per Casa C (es. 'Casa Parco')", "Casa C")
        alternatives = [casa_a_nome, casa_b_nome, casa_c_nome]

        # Lista di fattori: rimosso "Costo dell'assicurazione" e aggiunti nuovi fattori
        factors = [
            "Prezzo",
            "Distanza dalla scuola",
            "Vicinanza ai trasporti pubblici",
            "Sicurezza del quartiere",
            "Numero di camere",
            "Spazio esterno",
            "Condizioni della casa",
            "Anno di costruzione",
            "Costi di manutenzione",
            "Prossimità a servizi essenziali (supermercato, ospedale)",
            "Qualità della scuola nel quartiere",
            "Accessibilità ai servizi",
            "Tranquillità della zona",
            "Valore di rivendita",
            "Facilità di finanziamento",
            "Disponibilità di parcheggio",
            "Dimensione complessiva",
            "Livello di inquinamento",
            "Vicino a spazi verdi",
            "Parere dei figli",
            "Costi d'ingresso",
            "Numero di bagni",                   # Nuovo fattore 1
            "Quanto piace alla nonna Manu",      # Nuovo fattore 2
            "Quanto piace al nonno",              # Nuovo fattore 3
            "Come sarà la casa tra 10 anni?",      # Nuovo fattore 4
            "Facilità di rivendita futura"         # Nuovo fattore 5
        ]

        st.header("Assegna pesi ai fattori")
        st.write("Indica l'importanza di ciascun fattore (1 = meno importante, 10 = importantissimo)")
        weights = {}
        for factor in factors:
            weights[factor] = st.slider(f"Peso per '{factor}'", 1, 10, 5)

        # Scegli il metodo di valutazione
        st.header("Metodo di valutazione")
        evaluation_method = st.radio(
            "Come preferisci valutare le case?",
            ["Valuta un fattore alla volta per tutte le case", "Valuta una casa alla volta per tutti i fattori"]
        )

        data = {alt: [0] * len(factors) for alt in alternatives}

        # Testo unificato per il fattore "Come sarà la casa tra 10 anni?"
        casa10_info = (" (Considera: dimensioni, flessibilità degli spazi, possibilità di modifiche future, "
                       "e pensa a chi abiterà la casa in futuro (es. chi resterà, chi andrà all'università o vivrà altrove e tornerà nel weekend); "
                       "punteggio basso se troppo grande o troppo piccolo)")

        st.header("Valutazione delle case")
        if evaluation_method == "Valuta un fattore alla volta per tutte le case":
            for i, factor in enumerate(factors):
                extra_info = ""
                if factor.strip().lower() == "come sarà la casa tra 10 anni?".lower():
                    extra_info = casa10_info
                elif factor == "Facilità di rivendita futura":
                    extra_info = " (Considera: ubicazione, trend di mercato, vicinanza a servizi e attrattiva per futuri acquirenti)"
                st.subheader(f"Valutazione per '{factor}'")
                st.write(f"Assegna un punteggio da 1 a 10 per ciascuna casa rispetto a '{factor}'{extra_info}")

                cols = st.columns(3)
                for j, alt in enumerate(alternatives):
                    with cols[j]:
                        data[alt][i] = st.slider(f"{alt}", 1, 10, 5, key=f"{factor}_{alt}")
        else:
            for alt in alternatives:
                st.subheader(f"Valutazione per {alt}")
                st.write(f"Assegna un punteggio da 1 a 10 per {alt} rispetto a ciascun fattore")
                for i, factor in enumerate(factors):
                    extra_info = ""
                    if factor.strip().lower() == "come sarà la casa tra 10 anni?".lower():
                        extra_info = casa10_info
                    elif factor == "Facilità di rivendita futura":
                        extra_info = " (Considera: ubicazione, stato di conservazione, vicinanza a servizi e attrattiva per futuri acquirenti)"
                    data[alt][i] = st.slider(f"'{factor}'{extra_info}", 1, 10, 5, key=f"{alt}_{factor}")

        # Bottone per mostrare i risultati
        if st.button("MOSTRA I RISULTATI", key="show_results"):
            # Calcolo dei punteggi ponderati
            df = pd.DataFrame(data, index=factors)
            weighted_scores = {}
            weight_series = pd.Series(weights)
            for alt in alternatives:
                weighted_sum = sum(df[alt][i] * weight_series[factor] for i, factor in enumerate(factors))
                weighted_scores[alt] = weighted_sum

            ranking = sorted(weighted_scores.items(), key=lambda x: x[1], reverse=True)

            st.header("Risultati")
            df_display = df.copy()
            df_display.insert(0, "Peso", weight_series)

            st.subheader("Matrice Decisionale")
            st.dataframe(df_display)

            st.subheader("Punteggi Ponderati")
            weighted_df = pd.DataFrame({
                'Alternativa': [alt for alt, _ in weighted_scores.items()],
                'Punteggio': [score for _, score in weighted_scores.items()]
            })
            weighted_df = weighted_df.sort_values('Punteggio', ascending=False)
            st.dataframe(weighted_df)

            st.subheader("Classifica delle Alternative")
            for i, (alt, score) in enumerate(ranking, start=1):
                st.write(f"{i}. **{alt}** - punteggio: {score:.2f}")

            st.subheader("Grafico comparativo")
            st.bar_chart(weighted_df.set_index('Alternativa'))

            winner = ranking[0][0]
            st.subheader(f"Perché {winner} è la scelta migliore")

            top_factors = []
            for factor in factors:
                factor_score = df[winner][factors.index(factor)] * weights[factor]
                top_factors.append((factor, factor_score))
            top_factors.sort(key=lambda x: x[1], reverse=True)

            st.write("Punti di forza:")
            for factor, score in top_factors[:3]:
                st.write(f"- **{factor}**: punteggio {df[winner][factors.index(factor)]}/10 × peso {weights[factor]} = {score:.1f} punti")

            # Genera il file Excel in memoria con il nome dell'utente in alto
            excel_buffer = io.BytesIO()

            # Aggiungi una riga "Totale" al dataframe, con i punteggi totali per ogni alternativa.
            # Lascia vuota la colonna "Peso"
            totals = [weighted_scores[alt] for alt in alternatives]
            df_display.loc["Totale"] = [""] + totals

            # Usa ExcelWriter per creare un foglio che include una sezione info con il nome utente
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                # Scrivi le informazioni dell'utente nella prima parte (es. riga 0)
                info_df = pd.DataFrame([f"Utente: {st.session_state.user_name}"])
                info_df.to_excel(writer, index=False, header=False, startrow=0)
                # Lascia una riga vuota (riga 1) e una riga vuota (riga 2)
                # Scrivi la matrice decisionale a partire dalla riga 3
                df_display.to_excel(writer, startrow=3, index=True)

            excel_buffer.seek(0)  # Torna all'inizio del buffer

            st.download_button(
                label="Scarica i risultati come Excel",
                data=excel_buffer,
                file_name='decision_matrix_results.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

            # Invia il file Excel via Telegram al bot
            bot_token = st.secrets.telegram.bot_token  # Token dal file secrets
            chat_id = st.secrets.telegram.chat_id          # Chat ID dal file secrets
            telegram_url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
            files = {"document": ("decision_matrix_results.xlsx", excel_buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            data_payload = {"chat_id": chat_id}
            response = requests.post(telegram_url, data=data_payload, files=files)
            if response.status_code == 200:
                st.success("Dati generati correttamente!")
            else:
                st.error("Errore nell'invio del file Excel a Telegram.")

if __name__ == "__main__":
    main()
