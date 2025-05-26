function initPlayground(codeAreaId, runButtonId, outputAreaId) {
    const codeArea = document.getElementById(codeAreaId);
    const runButton = document.getElementById(runButtonId);
    const outputArea = document.getElementById(outputAreaId);

    if (!codeArea || !runButton || !outputArea) {
        console.error("JS Playground: One or more element IDs not found.", { codeAreaId, runButtonId, outputAreaId });
        return;
    }

    runButton.addEventListener('click', function() {
        const userCode = codeArea.value;
        outputArea.innerHTML = ''; // Clear previous output

        const capturedLogs = [];

        // Store original console functions
        const originalConsole = {
            log: console.log,
            error: console.error,
            warn: console.warn,
            info: console.info,
        };

        // Override console functions
        console.log = function(...args) {
            capturedLogs.push({ type: 'LOG', content: args.map(arg => String(arg)).join(' ') });
            originalConsole.log.apply(console, args); // Still log to actual browser console if desired
        };
        console.error = function(...args) {
            capturedLogs.push({ type: 'ERROR', content: args.map(arg => String(arg)).join(' ') });
            originalConsole.error.apply(console, args);
        };
        console.warn = function(...args) {
            capturedLogs.push({ type: 'WARN', content: args.map(arg => String(arg)).join(' ') });
            originalConsole.warn.apply(console, args);
        };
        console.info = function(...args) {
            capturedLogs.push({ type: 'INFO', content: args.map(arg => String(arg)).join(' ') });
            originalConsole.info.apply(console, args);
        };

        try {
            // Execute the user's code
            // Using a new Function constructor.
            // The code runs in its own scope but can access global variables.
            // For more isolation, a Web Worker or iframe sandbox would be better.
            const F = new Function(userCode);
            F();
        } catch (e) {
            capturedLogs.push({ type: 'EXCEPTION', content: `${e.name}: ${e.message}` });
        } finally {
            // Restore original console functions
            console.log = originalConsole.log;
            console.error = originalConsole.error;
            console.warn = originalConsole.warn;
            console.info = originalConsole.info;

            // Display captured logs in the output area
            capturedLogs.forEach(log => {
                const logEntry = document.createElement('div');
                logEntry.textContent = `${log.type}: ${log.content}`;
                if (log.type === 'ERROR' || log.type === 'EXCEPTION') {
                    logEntry.style.color = 'red';
                } else if (log.type === 'WARN') {
                    logEntry.style.color = 'orange';
                }
                outputArea.appendChild(logEntry);
            });
        }
    });

    console.log(`JS Console Playground initialized for codeArea: ${codeAreaId}, runButton: ${runButtonId}, outputArea: ${outputAreaId}`);
}
