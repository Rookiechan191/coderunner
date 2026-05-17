export const LANGUAGES = {
  python: {
    monacoLang: "python",
    color: "#3572A5",
    starter: `print("Hello, World!")`,
  },
  javascript: {
    monacoLang: "javascript",
    color: "#f1e05a",
    starter: `console.log("Hello, World!");`,
  },
  go: {
    monacoLang: "go",
    color: "#00ADD8",
    starter: `package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, World!")\n}`,
  },
  java: {
    monacoLang: "java",
    color: "#b07219",
    starter: `public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}`,
  },
  rust: {
    monacoLang: "rust",
    color: "#dea584",
    starter: `fn main() {\n    println!("Hello, World!");\n}`,
  },
  cpp: {
    monacoLang: "cpp",
    color: "#f34b7d",
    starter: `#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello, World!" << endl;\n    return 0;\n}`,
  },
}