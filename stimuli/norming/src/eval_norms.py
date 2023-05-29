import numpy as np
import pandas as pd


def main():
    samples = pd.read_csv("../materials/norm_samples.csv").dropna()
    logprobs = pd.read_csv("../materials/norm_all_text-davinci-003_results.csv")
    log10p_yes = []
    log10p_no = []
    for i, row in samples.iterrows():
        sample = f"Object:\n{row.object}\nCategory:\n{row.category}\nResponse:"
        scores = logprobs[logprobs["text"] == sample]
        log10p_yes.append(scores[scores["query"] == "yes"].logp.values[0])
        log10p_no.append(scores[scores["query"] == "no"].logp.values[0])
    samples["logp_vocab_yes"] = log10p_yes / np.log10(np.exp(1))
    samples["logp_vocab_no"] = log10p_no / np.log10(np.exp(1))
    samples["p_vocab_yes_or_no"] = np.exp(
        np.logaddexp(samples["logp_vocab_yes"], samples["logp_vocab_no"])
    )
    samples["p_scaled_yes"] = (
        np.exp(samples["logp_vocab_yes"]) / samples["p_vocab_yes_or_no"]
    )
    samples["p_scaled_no"] = (
        np.exp(samples["logp_vocab_no"]) / samples["p_vocab_yes_or_no"]
    )
    samples.to_csv("../materials/norms.csv", index=False)


if __name__ == "__main__":
    main()
