def interpret_data(data, model, tokenizer):
    prompt = (
        "Interpret the given data and provide me the description for the data:\n"
        f"{data.columns}\n{data.head()}"
    )

    inputs = tokenizer.encode(prompt, return_tensors="pt")

    # Generate response from the model
    outputs = model.generate(inputs, max_length=150, num_beams=5, temperature=0.7)
    
    # Decode the generated response
    response_message = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return response_message.strip()

def main():
    st.title("Data Interpretation with Hugging Face Llama Model")

    # Load Llama model and tokenizer
    name = "meta-llama/Llama-2-70b-chat-hf"
    auth_token = "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"
    tokenizer = AutoTokenizer.from_pretrained(name, cache_dir='./model/', use_auth_token=auth_token)
    model = AutoModelForCausalLM.from_pretrained(name, cache_dir='./model/'
                        , use_auth_token=auth_token, 
                        rope_scaling={"type": "dynamic", "factor": 2}, load_in_8bit=True) 

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.write("### Uploaded Data:")
        st.write(data)

        interpretation = interpret_data(data, model, tokenizer)
        st.write("### Data Interpretation:")
        st.write(interpretation)

if __name__ == "__main__":
    main()