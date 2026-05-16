export const LANGUAGES = {
  python: {
    label: "Python",
    monacoLang: "python",
    color: "#3b82f6",
    starter: `def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        print(a, end=" ")
        a, b = b, a + b
    print()

fibonacci(10)
`,
  },
  javascript: {
    label: "JavaScript",
    monacoLang: "javascript",
    color: "#eab308",
    starter: `function fibonacci(n) {
  let [a, b] = [0, 1];
  for (let i = 0; i < n; i++) {
    process.stdout.write(a + " ");
    [a, b] = [b, a + b];
  }
  console.log();
}
fibonacci(10);
`,
  },
  go: {
    label: "Go",
    monacoLang: "go",
    color: "#06b6d4",
    starter: `package main

import "fmt"

func main() {
    a, b := 0, 1
    for i := 0; i < 10; i++ {
        fmt.Printf("%d ", a)
        a, b = b, a+b
    }
    fmt.Println()
}
`,
  },
  rust: {
    label: "Rust",
    monacoLang: "rust",
    color: "#f97316",
    starter: `fn main() {
    let (mut a, mut b) = (0u64, 1u64);
    for _ in 0..10 {
        print!("{} ", a);
        (a, b) = (b, a + b);
    }
    println!();
}
`,
  },
  java: {
    label: "Java",
    monacoLang: "java",
    color: "#ef4444",
    starter: `public class Main {
    public static void main(String[] args) {
        long a = 0, b = 1;
        for (int i = 0; i < 10; i++) {
            System.out.print(a + " ");
            long tmp = a + b;
            a = b;
            b = tmp;
        }
        System.out.println();
    }
}
`,
  },
};
