from sentence_transformers import SentenceTransformer, CrossEncoder
from database_connection import get_connection

# 1. Load the same model used during ingestion
model = SentenceTransformer("all-MiniLM-L6-v2")

# Reranking/ read the question and each document together and produce a relevence score
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

score = reranker.predict([
    ["What is a factless fact tables?", "A factless fact table contains only dimension keys"],
    ["What is a factless fact tables?", "For more information, see the documentions"]
])
print(score)



while True:
    # 2. Ask the question
    question = input("\nAsk a PowerBI question or exit : ").strip()    

    if question.lower() == "exit":
        print("Thanks")
        break
    else:   

        # 3. Convert the question into vector
        question_embedding = model.encode(question)

        #4. Connect to PostgreSQL
        with get_connection() as conn:
            with conn.cursor() as cursor:

                #. Find the first 3 most similar chunks
                cursor.execute(
                """
                SELECT 
                    d.title, 
                    d.source_url,
                    dc.section_heading,
                    dc.content, 
                    dc.embedding <=> %s AS distance
                FROM document_chunks dc
                JOIN documents d
                    ON dc.document_id = d.id
                WHERE dc.embedding IS NOT NULL
                ORDER BY dc.embedding <=> %s 
                LIMIT 10
                """,
                (question_embedding, question_embedding)
                
                )

                results = cursor.fetchall()

        # Prepare question-document pairs for reranking
        pairs = []

        for title, source_url, heading, content, distance in results:
            pairs.append((question, heading + "\n" + content))
            

        #calculating the ranking score using CrossEncoder
        ranked_result = []

        if pairs:
            scores = reranker.predict(pairs)

            for result, score in zip(results, scores):
                title, source_url, heading, content, distance = result

    

                ranked_result.append((title, source_url, heading, content, distance, float(score)))

        #Sort by ranking score highest to lowest
        ranked_result.sort(key=lambda item: item[5], reverse=True)

        #Select the top 3 chunks
        top_results = ranked_result[:3]


        #Display result
        for title, source_url, heading, content, distance, score in top_results:
            print("-------------------------------------->")
            print("\nTitle : ", title)
            print("\nSource_url : ", source_url )
            print("\nSection : ", heading)
            print("Content : ", content)
            print("Distance : ", distance)
            print("Score : ", score)

    print("---------------------------------------------")
    print("---------------------------------------------")