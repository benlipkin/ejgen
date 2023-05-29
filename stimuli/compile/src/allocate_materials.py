import json
import pandas as pd


def load_materials():
    materials = pd.read_csv("../materials/ejgen_materials.csv")
    for col in ["exemplars", "targets"]:
        materials[col] = materials[col].apply(lambda x: json.loads(x.replace("'", '"')))
    return materials


def prepare_stim_table(stim_batch):
    stimuli = stim_batch.loc[
        :,
        [
            "stimulus_group",
            "exemplar_condition",
            "target_condition",
            "category_condition",
            "stimulus_construction",
            "targets",
        ],
    ].rename(
        columns={
            "stimulus_group": "group",
            "stimulus_construction": "concept",
            "targets": "target",
        }
    )
    stimuli["stimulus"] = (
        "Imagine there is a rule that states it applies to '"
        + stimuli["concept"]
        + ".' Do you think that the rule applies to '"
        + stimuli["target"]
        + "'?"
    )
    return stimuli.sample(frac=1, random_state=0).reset_index(drop=True)


def main():
    materials = load_materials()
    for _, stim_group in materials.groupby("stimulus_group"):
        n_targets = stim_group.targets.apply(len)
        assert len(set(n_targets)) == 1
        for target_idx in range(n_targets.values[0]):
            stim_batch = stim_group.copy()
            stim_batch["targets"] = stim_batch["targets"].apply(lambda x: x[target_idx])
            stimuli = prepare_stim_table(stim_batch)
            fname = f"../materials/stims_{stimuli['group'].values[0]+target_idx*materials['stimulus_group'].unique().size+1:02d}.csv"
            stimuli.to_csv(fname, index=False)


if __name__ == "__main__":
    main()
