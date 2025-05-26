function initCodingExercise(exerciseDataJson, testCasesJson, codeAreaId, runButtonId, resultsAreaId, submissionFormId) {
    const exerciseData = JSON.parse(exerciseDataJson);
    const testCases = JSON.parse(testCasesJson);

    const codeArea = document.getElementById(codeAreaId);
    const runButton = document.getElementById(runButtonId);
    const resultsArea = document.getElementById(resultsAreaId);
    const submissionForm = document.getElementById(submissionFormId);
    
    const passedTestsInput = submissionForm.querySelector('input[name="passed_tests"]');
    const totalTestsInput = submissionForm.querySelector('input[name="total_tests"]');
    const submitButton = submissionForm.querySelector('button[type="submit"]');


    if (!codeArea || !runButton || !resultsArea || !submissionForm || !passedTestsInput || !totalTestsInput || !submitButton) {
        console.error("Coding Exercise DOM elements not found. Check IDs.", {
            codeAreaId, runButtonId, resultsAreaId, submissionFormId
        });
        return;
    }
    
    // Pre-fill with starter code or a basic template
    if (exerciseData.starter_code) {
        codeArea.value = exerciseData.starter_code;
    } else {
        codeArea.value = `function ${exerciseData.function_name || 'solve'}(/* parameters */) {\n  // Your code here\n  \n}`;
    }
    
    submitButton.disabled = true; // Disable submit until tests are run at least once

    runButton.addEventListener('click', function() {
        const userCode = codeArea.value;
        resultsArea.innerHTML = ''; // Clear previous results
        let passedCount = 0;
        let resultsDetails = [];

        testCases.forEach((testCase, index) => {
            const resultItem = document.createElement('div');
            resultItem.classList.add('test-result-item');
            let status = 'Errored';
            let actualOutputDisplay = 'N/A';

            try {
                const args = JSON.parse(testCase.input_data || '[]');
                const expectedOutput = JSON.parse(testCase.expected_output);
                
                // Create the function from user's code.
                // This is a simplified and somewhat risky way to do it.
                // It assumes userCode defines a function with exerciseData.function_name
                // A safer method would involve Web Workers or a more robust sandboxed eval.
                const userFunc = new Function(userCode + `; return ${exerciseData.function_name};`)();

                if (typeof userFunc !== 'function') {
                    throw new Error(`Function '${exerciseData.function_name}' not found or not a function.`);
                }

                const actualOutput = userFunc.apply(null, args);
                actualOutputDisplay = JSON.stringify(actualOutput); // For display

                // Basic comparison, for complex objects/arrays, a deep equal function would be better
                if (JSON.stringify(actualOutput) === JSON.stringify(expectedOutput)) {
                    status = 'Passed';
                    passedCount++;
                    resultItem.classList.add('passed');
                } else {
                    status = 'Failed';
                    resultItem.classList.add('failed');
                }
                resultsDetails.push({
                    input: testCase.input_data,
                    expected: testCase.expected_output,
                    actual: actualOutputDisplay,
                    status: status
                });

            } catch (e) {
                status = 'Errored';
                actualOutputDisplay = e.toString();
                resultItem.classList.add('errored');
                resultsDetails.push({
                    input: testCase.input_data,
                    expected: testCase.expected_output,
                    actual: actualOutputDisplay,
                    status: status
                });
            }
            resultItem.innerHTML = `<strong>Test Case ${index + 1} (${testCase.description || ''}): ${status}</strong><br>
                                   Input: <code>${testCase.input_data}</code><br>
                                   Expected: <code>${testCase.expected_output}</code><br>
                                   Actual: <code>${actualOutputDisplay}</code>`;
            resultsArea.appendChild(resultItem);
        });

        const summary = document.createElement('h5');
        summary.textContent = `Overall: Passed ${passedCount} out of ${testCases.length} tests.`;
        resultsArea.insertBefore(summary, resultsArea.firstChild);
        
        // Update hidden form fields
        passedTestsInput.value = passedCount;
        totalTestsInput.value = testCases.length;
        
        // Enable submit button
        submitButton.disabled = false; 
        // Store results details (optional, if you want to send them to server)
        const resultsDetailsInput = submissionForm.querySelector('input[name="results_details"]');
        if (resultsDetailsInput) {
            resultsDetailsInput.value = JSON.stringify(resultsDetails);
        }
    });
    console.log("Coding exercise environment initialized for exercise: " + exerciseData.exercise_id);
}
