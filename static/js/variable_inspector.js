function initInspector(codeAreaId, runButtonId, outputAreaId, variablesAreaId) {
    const codeArea = document.getElementById(codeAreaId);
    const runButton = document.getElementById(runButtonId);
    const outputArea = document.getElementById(outputAreaId);
    const variablesArea = document.getElementById(variablesAreaId);

    if (!codeArea || !runButton || !outputArea || !variablesArea) {
        console.error("Variable Inspector: One or more element IDs not found.", { codeAreaId, runButtonId, outputAreaId, variablesAreaId });
        return;
    }

    runButton.addEventListener('click', function() {
        const userCode = codeArea.value;
        outputArea.innerHTML = ''; // Clear previous output
        variablesArea.innerHTML = ''; // Clear previous variable states

        const variableStates = {};
        const lines = userCode.split('\n');

        // Regex for declarations: let x = 10; var y = "hello"; const z = true;
        const declarationRegex = /^(?:let|var|const)\s+([a-zA-Z_]\w*)\s*=\s*(.+);?$/;
        // Regex for assignments: x = 20;
        const assignmentRegex = /^([a-zA-Z_]\w*)\s*=\s*(.+);?$/;
        // Regex for console.log: console.log(message); console.log("message");
        const consoleLogRegex = /^console\.log\((.*)\);?$/;

        function logToOutput(message, isError = false) {
            const logEntry = document.createElement('div');
            logEntry.textContent = message;
            if (isError) {
                logEntry.style.color = 'red';
            }
            outputArea.appendChild(logEntry);
        }

        function evaluateValue(valueStr, currentStates) {
            valueStr = valueStr.trim();
            // Boolean
            if (valueStr === "true") return true;
            if (valueStr === "false") return false;
            // Number
            if (!isNaN(valueStr) && valueStr !== "") return parseFloat(valueStr);
            // String literal
            if ((valueStr.startsWith('"') && valueStr.endsWith('"')) || (valueStr.startsWith("'") && valueStr.endsWith("'"))) {
                return valueStr.slice(1, -1);
            }
            // Variable reference (very basic, direct reference only)
            if (currentStates.hasOwnProperty(valueStr)) {
                return currentStates[valueStr];
            }
            // For more complex expressions like 'x + 5', more advanced parsing or a safer eval is needed.
            // This version keeps it simple: only literals or direct variable references.
            logToOutput(`Error: Cannot evaluate value: '${valueStr}'. Only numbers, string literals (e.g., "hello"), booleans (true/false), or existing variables are supported for assignment.`, true);
            throw new Error("EvaluationError"); 
        }
        
        for (const line of lines) {
            const trimmedLine = line.trim();
            if (trimmedLine === "") continue;

            try {
                let match;
                if (match = trimmedLine.match(declarationRegex)) {
                    // Declaration: let x = 10;
                    const varName = match[1];
                    const valueStr = match[2];
                    variableStates[varName] = evaluateValue(valueStr, variableStates);
                } else if (match = trimmedLine.match(assignmentRegex)) {
                    // Assignment: x = 20;
                    const varName = match[1];
                    if (!variableStates.hasOwnProperty(varName)) {
                        logToOutput(`Error: Variable '${varName}' not declared before assignment. (Use let/var/const to declare)`, true);
                        break; 
                    }
                    const valueStr = match[2];
                    variableStates[varName] = evaluateValue(valueStr, variableStates);
                } else if (match = trimmedLine.match(consoleLogRegex)) {
                    // console.log(message);
                    const argStr = match[1].trim();
                    if ((argStr.startsWith('"') && argStr.endsWith('"')) || (argStr.startsWith("'") && argStr.endsWith("'"))) {
                        logToOutput(`LOG: ${argStr.slice(1, -1)}`);
                    } else if (variableStates.hasOwnProperty(argStr)) {
                        logToOutput(`LOG: ${variableStates[argStr]}`);
                    } else {
                        logToOutput(`LOG Error: console.log argument '${argStr}' is not a string literal or known variable.`, true);
                    }
                } else {
                    logToOutput(`Error: Unsupported syntax or typo on line: "${trimmedLine}"`, true);
                    break; // Stop processing on error
                }
            } catch (e) {
                if (e.message !== "EvaluationError") { // EvaluationError already logged
                    logToOutput(`Runtime Error: ${e.message}`, true);
                }
                break; // Stop processing on any error
            }
        }

        // Display variable states
        for (const varName in variableStates) {
            if (variableStates.hasOwnProperty(varName)) {
                const value = variableStates[varName];
                const type = typeof value;
                const varEntry = document.createElement('div');
                varEntry.innerHTML = `<strong>${varName}</strong>: ${value} (<em>${type}</em>)`;
                variablesArea.appendChild(varEntry);
            }
        }
    });
    console.log(`Variable Inspector initialized for codeArea: ${codeAreaId}`);
}
