// Route evidence before importing live app configuration, discovery or Playwright.
if (process.argv.slice(2).some(arg => arg === "--evidence" || arg.startsWith("--evidence="))) {
  import("./evidence-cli").then(module => module.main()).catch(error => {
    console.error(String(error)); process.exitCode = 2;
  });
} else {
  import("./prove-live");
}
export {};
