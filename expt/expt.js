// Ejusdem Generis JsPsych Experiment Frontend

function build_general_instructions() {
  return {
    type: jsPsychInstructions,
    pages: [
      `
      <p>Welcome!</p>
      <p>We are conducting an experiment about language comprehension.
      Your answers will be used to inform scientific research.</p>
      <p>This experiment should take at most <b>10 minutes</b>. You will be compensated at a base rate 
      of $15.00/hour for a total of <b>$2.50</b>, which you will receive as long as you complete the study.</p>
      <p> We take your compensation and time seriously! The email for the main experimenter is <b>mitcpllab@gmail.com</b>. 
      Please write this down now, and email us with your Prolific ID and the subject line "Prolific Experiment" 
      if you have problems submitting this task, or if it takes much more time than expected.</p>
      <p>This experiment must be completed in <b>full-screen</b> in order to view all the required components. 
      Please make sure you are set up, and then press <b>"Next"</b> when ready to read the task instructions.</p>
      `,
    ],
    show_clickable_nav: true,
  };
}

function prep_task_instructions() {
  return {
    type: jsPsychInstructions,
    pages: [
      `
      <p>In this experiment, you will be reading descriptions of a category to which a hypothetical rule applies.</p>
      <p>For each category description, you will be shown a new example to which the rule may or may not apply.</p>
      <p>Your task will be to respond <em>Yes</em> or <em>No</em> whether you think the rule applies to that new example.</p>
      <p>Some of the trials will feel difficult to decide definitively on, and that's okay! Simply choose what you think to be the best response.</p>
      <br>
      <p>Press <b>"Next"</b> to complete a quick comprehension check.</p>
      `,
    ],
    show_clickable_nav: true,
  };
}

function prep_Q0() {
  return {
    prompt: "What will you be doing in this task?",
    options: [
      "Reading descriptions about the category to which a rule applies.",
      "Reading descriptions of rules and determining whether they are fair.",
      "Writing descriptions of rules as summaries.",
    ],
    required: true,
  };
}

function prep_Q1() {
  return {
    prompt:
      "For each described category, you will be asked about a new example. This example will: ",
    options: [
      "Always be in the described category.",
      "Never be in the described category.",
      "Sometimes be in the described category.",
    ],
    required: true,
  };
}

function prep_Q2() {
  return {
    prompt: "In order to complete each trial, you will need to: ",
    options: [
      "Move a slider to indicate your confidence level.",
      "Respond <em>Yes</em> or <em>No</em>.",
      "Write your response in a text box.",
    ],
    required: true,
  };
}

function prep_task_comprehension_check() {
  return {
    type: jsPsychSurveyMultiChoice,
    preamble: [
      "<p>Check your knowledge before you begin. If you get one or more questions wrong, don't worry; we will show you the instructions again.</p>",
    ],
    questions: [prep_Q0(), prep_Q1(), prep_Q2()],
    on_finish: function (data) {
      var responses = data.response;
      if (
        responses["Q0"] ==
          "Reading descriptions about the category to which a rule applies." &&
        responses["Q1"] == "Sometimes be in the described category." &&
        responses["Q2"] == "Respond <em>Yes</em> or <em>No</em>."
      ) {
        correct = true;
      } else {
        correct = false;
      }
    },
  };
}

function build_task_instructions() {
  return {
    timeline: [prep_task_instructions(), prep_task_comprehension_check()],
    loop_function: function (data) {
      return !correct;
    },
  };
}

function build_final_instructions(n_trials) {
  return {
    type: jsPsychInstructions,
    pages: [
      `
      <p>You are now about to begin the experiment.</p>
      <p>There will be ${n_trials} trials.</p>
      <p>As a reminder, you should evaluate each trial separately, and respond only based on that trial.</p>
      <p>Please click <b>"Next"</b> to start the experiment.</p>
      `,
    ],
    show_clickable_nav: true,
  };
}

function prep_trial_structure(jsPsych, n_trials) {
  return {
    type: jsPsychSurveyLikert,
    questions: [
      {
        prompt: jsPsych.timelineVariable("stimulus"),
        labels: ["No", "Yes"],
        required: true,
        horizontal: true,
      },
    ],
    data: {
      stimulus: jsPsych.timelineVariable("stimulus")
    },
    on_finish: function () {
      jsPsych.setProgressBar(jsPsych.getProgressBarCompleted() + 1 / n_trials);
    },
  };
}

function build_trials(jsPsych, stimuli) {
  return {
    timeline: [prep_trial_structure(jsPsych, stimuli.length)],
    timeline_variables: stimuli,
    repetitions: 1,
    randomize_order: true,
  };
}

function build_comments_block() {
  return {
    type: jsPsychSurveyText,
    preamble: `
          <p>Thank you for participating in our study!</p>
          <p>Click "Finish" to complete the experiment and receive compensation. 
          If you have any comments about the experiment, please let us know in the form below.</p>`,
    questions: [
      {
        prompt:
          "Were the instructions clear? (On a scale of 1-10, with 10 being very clear)",
      },
      {
        prompt:
          "How challenging was it to determine whether the new example was part of the category? (On a scale of 1-10, with 10 being very challenging)",
      },
      { prompt: "Did you get bored during the task? (Yes, No, or Sort of)" },
      {
        prompt: "Do you have any additional comments to share with us?",
        rows: 5,
        columns: 50,
      },
    ],
    button_label: "Finish",
  };
}

function build_timeline(jsPsych, stimuli) {
  var timeline = [];
  timeline.push(build_general_instructions());
  timeline.push(build_task_instructions());
  timeline.push(build_final_instructions(stimuli.length));
  timeline.push(build_trials(jsPsych, stimuli));
  timeline.push(build_comments_block());
  return timeline;
}

function run_expt(stimuli, id) {
  const jsPsych = initJsPsych({
    on_finish: function () {
      fetch("", { // TODO: post completion to server
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ stim_id: id }),
      }).then((response) => {
        window.location = "https://www.prolific.co/"; // TODO: add prolific redirect
      });
    },
    show_progress_bar: true,
    auto_update_progress_bar: false,
  });
  jsPsych.data.addProperties({
    subject_id: jsPsych.data.getURLVariable("PROLIFIC_PID"),
    study_id: jsPsych.data.getURLVariable("STUDY_ID"),
    session_id: jsPsych.data.getURLVariable("SESSION_ID"),
  });
  timeline = build_timeline(jsPsych, stimuli);
  jsPsych.run(timeline);
}

function main() {
  fetch("") // TODO: get stimuli from server
    .then((response) => response.json())
    .then((data) => {
      stimuli = data["stim_contents"];
      id = data["stim_id"];
      run_expt(stimuli, id);
    });
}

main();
