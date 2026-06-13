const runBtn = document.getElementById('run-btn');
const outputBox = document.getElementById('output');
const statusBox = document.getElementById('status');
const traceBox = document.getElementById('trace');
const metricsBox = document.getElementById('metrics');
const citationsBox = document.getElementById('citations');
const privacyBox = document.getElementById('privacy');
const approvalNote = document.getElementById('approval-note');
const approveBtn = document.getElementById('approve-btn');
const scenarioInput = document.getElementById('scenario');

function updateApprovalAvailability() {
  const ready = outputBox.dataset.result === 'ready';
  approveBtn.disabled = !ready;
  approveBtn.style.opacity = ready ? '1' : '0.55';
  approveBtn.style.cursor = ready ? 'pointer' : 'not-allowed';
}

function setStatus(message, tone = 'info') {
  statusBox.textContent = message;
  statusBox.dataset.tone = tone;
}

async function runWorkflow() {
  setStatus('Running the planner → analyst → operations workflow…', 'info');
  outputBox.dataset.result = 'loading';
  outputBox.textContent = 'Working…';
  updateApprovalAvailability();

  try {
    const response = await fetch('/run-workflow', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario: scenarioInput.value.trim() || 'Cappuccino sales dropped 15% in the morning. Recommend the next operational step.' })
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || 'Workflow run failed.');
    }

    const formattedOutput = payload.output
      .replace(/(-\d+(?:\.\d+)?%)/g, '<span class="negative-result">$1</span>')
      .replace(/(Biggest decline:.*?\n)/g, '<span class="negative-result">$1</span>');
    outputBox.innerHTML = formattedOutput;
    outputBox.dataset.result = 'ready';
    traceBox.textContent = payload.trace.join('\n');
    metricsBox.textContent = `Confidence Score: ${payload.confidence}%\nExpected ROI: ${payload.roi}`;
    citationsBox.textContent = payload.citations.join('\n');
    privacyBox.textContent = payload.privacy;
    updateApprovalAvailability();
    setStatus('Workflow completed successfully.', 'success');
  } catch (error) {
    outputBox.textContent = `Error: ${error.message}`;
    outputBox.dataset.result = 'error';
    traceBox.textContent = 'No trace available.';
    metricsBox.textContent = 'No metrics available.';
    citationsBox.textContent = 'No citations available.';
    privacyBox.textContent = 'Synthetic data only.';
    updateApprovalAvailability();
    setStatus('Workflow run failed. Check the terminal output for details.', 'error');
  }
}

runBtn?.addEventListener('click', runWorkflow);
outputBox.dataset.result = 'idle';
updateApprovalAvailability();
approveBtn?.addEventListener('click', () => {
  if (!approveBtn.disabled) {
    approvalNote.textContent = 'Approved by human-in-the-loop reviewer. Launch can proceed in a hosted environment.';
  }
});
