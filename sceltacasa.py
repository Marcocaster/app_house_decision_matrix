import pandas as pd
import streamlit as st


def main():
    st.title("Decision Matrix per la scelta della casa dell anonna manu e nipotazzi")
    st.subheader(
        "Considerazioni per una donna single con 3 figli, budget limitato e necessità di spostamenti per la scuola.")

    # Permettere all'utente di personalizzare i nomi delle case per renderli più facili da ricordare
    st.header("Personalizza i nomi delle case")
    st.write("Inserisci nomi più descrittivi per aiutarti a ricordare meglio le diverse opzioni")

    casa_a_nome = st.text_input("Nome per Casa A (es. 'Casa Centro')", "Casa A")
    casa_b_nome = st.text_input("Nome per Casa B (es. 'Casa Villetta')", "Casa B")
    casa_c_nome = st.text_input("Nome per Casa C (es. 'Casa Parco')", "Casa C")

    alternatives = [casa_a_nome, casa_b_nome, casa_c_nome]

    # Lista di fattori importanti predefiniti
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
        "Costo dell'assicurazione",
        "Livello di inquinamento",
        "Vicino a spazi verdi"

    ]

    st.header("Assegna pesi ai fattori")
    st.write("Prima di tutto, indica l'importanza di ciascun fattore nella tua decisione")
    st.write("Assegna un peso da 1 a 10 per ogni fattore (10 = più importante)")

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

    st.header("Valutazione delle case")
    if evaluation_method == "Valuta un fattore alla volta per tutte le case":
        # Approccio per fattori (orizzontale)
        for i, factor in enumerate(factors):
            st.subheader(f"Valutazione per '{factor}'")
            st.write(f"Assegna un punteggio da 1 a 10 per ciascuna casa rispetto a '{factor}'")

            cols = st.columns(3)
            for j, alt in enumerate(alternatives):
                with cols[j]:
                    data[alt][i] = st.slider(f"{alt}", 1, 10, 5, key=f"{factor}_{alt}")
    else:
        # Approccio per case (verticale)
        for alt in alternatives:
            st.subheader(f"Valutazione per {alt}")
            st.write(f"Assegna un punteggio da 1 a 10 per {alt} rispetto a ciascun fattore")

            for i, factor in enumerate(factors):
                data[alt][i] = st.slider(f"'{factor}'", 1, 10, 5, key=f"{alt}_{factor}")

    # Creazione del DataFrame della decision matrix
    df = pd.DataFrame(data, index=factors)

    # Calcolo dei punteggi ponderati
    weighted_scores = {}
    weight_series = pd.Series(weights)
    for alt in alternatives:
        weighted_sum = sum(df[alt][i] * weight_series[factor] for i, factor in enumerate(factors))
        weighted_scores[alt] = weighted_sum

    # Ordinamento delle alternative
    ranking = sorted(weighted_scores.items(), key=lambda x: x[1], reverse=True)

    st.header("Risultati")

    # Aggiungi una colonna dei pesi alla matrice di decisione
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

    # Visualizzazione grafica
    st.subheader("Grafico comparativo")
    st.bar_chart(weighted_df.set_index('Alternativa'))

    # Dettagli sul punteggio del vincitore
    winner = ranking[0][0]
    st.subheader(f"Perché {winner} è la scelta migliore")

    # Trova i 3 fattori più importanti in cui il vincitore eccelle
    top_factors = []
    for factor in factors:
        factor_score = df[winner][factors.index(factor)] * weights[factor]
        top_factors.append((factor, factor_score))

    top_factors.sort(key=lambda x: x[1], reverse=True)

    st.write("Punti di forza:")
    for factor, score in top_factors[:3]:
        st.write(
            f"- **{factor}**: punteggio {df[winner][factors.index(factor)]}/10 × peso {weights[factor]} = {score:.1f} punti")

    # Opzione per salvare i risultati
    if st.button("Salva risultati come CSV"):
        df_display.to_csv("decision_matrix_results.csv")
        st.success("Risultati salvati come 'decision_matrix_results.csv'")


if __name__ == "__main__":
    main()
