export interface Translation {
  jargon: string;
  explanation: string;
  category: string;
}

export const techTranslations: Translation[] = [
  // Development & Engineering
  { 
    jargon: "refactor", 
    explanation: "Fancy way of saying 'I'm gonna clean up this messy code so it doesn't look like a spaghetti monster wrote it'", 
    category: "Software Engineering" 
  },
  { 
    jargon: "technical debt", 
    explanation: "The tech equivalent of 'I'll clean my room tomorrow' - except tomorrow never comes and now you're buried in code chaos", 
    category: "Software Engineering" 
  },
  { 
    jargon: "MVP", 
    explanation: "The 'good enough' version of your app that you release to see if anyone actually wants it. Like testing if people will eat your cooking before you open a restaurant", 
    category: "Product Strategy" 
  },
  { 
    jargon: "scalable", 
    explanation: "System architecture capable of handling increased workloads through horizontal or vertical scaling without performance degradation", 
    category: "Architecture" 
  },
  { 
    jargon: "robust", 
    explanation: "System resilience characterized by fault tolerance, graceful failure handling, and consistent performance under adverse conditions", 
    category: "Architecture" 
  },
  { 
    jargon: "optimize", 
    explanation: "Performance enhancement through algorithmic improvements, resource utilization efficiency, and bottleneck elimination", 
    category: "Performance" 
  },
  { 
    jargon: "legacy code", 
    explanation: "Production code utilizing outdated technologies or patterns, requiring modernization to align with current architectural standards", 
    category: "Software Engineering" 
  },
  { 
    jargon: "code review", 
    explanation: "Quality assurance process involving peer evaluation of code changes to ensure standards compliance and knowledge sharing", 
    category: "Software Engineering" 
  },
  { 
    jargon: "hotfix", 
    explanation: "Expedited patch deployment addressing critical production issues outside normal release cycles", 
    category: "Operations" 
  },
  { 
    jargon: "rollback", 
    explanation: "Reverting system state to previous stable version using automated deployment pipelines to minimize service disruption", 
    category: "Operations" 
  },
  
  // Cloud & Infrastructure
  { 
    jargon: "microservices", 
    explanation: "Breaking your big app into tiny apps so when one crashes, the others don't care. Like having multiple backup plans for your backup plans", 
    category: "Architecture" 
  },
  { 
    jargon: "monolith", 
    explanation: "Single-unit application architecture where all components are interconnected and interdependent, deployed as one entity", 
    category: "Architecture" 
  },
  { 
    jargon: "load balancer", 
    explanation: "Network component distributing incoming requests across multiple servers to optimize resource utilization and prevent overload", 
    category: "Infrastructure" 
  },
  { 
    jargon: "API", 
    explanation: "The digital handshake that lets different apps talk to each other. Like a translator for computers that don't speak the same language", 
    category: "Integration" 
  },
  { 
    jargon: "containerization", 
    explanation: "Application packaging technology ensuring consistent execution environments across development, testing, and production infrastructures", 
    category: "DevOps" 
  },
  { 
    jargon: "orchestration", 
    explanation: "Automated management of containerized applications including deployment, scaling, networking, and service discovery", 
    category: "DevOps" 
  },
  { 
    jargon: "serverless", 
    explanation: "Running code without managing servers - like having a magical butler who only charges you when you actually use the bathroom", 
    category: "Cloud Computing" 
  },
  { 
    jargon: "edge computing", 
    explanation: "Distributed computing paradigm processing data closer to end users, reducing latency and bandwidth consumption", 
    category: "Infrastructure" 
  },
  { 
    jargon: "cloud computing", 
    explanation: "On-demand delivery of computing resources over the internet, enabling elastic scaling and operational cost optimization", 
    category: "Infrastructure" 
  },
  
  // Business & Strategy
  { 
    jargon: "synergy", 
    explanation: "Combined organizational capabilities producing outcomes greater than individual component contributions through strategic collaboration", 
    category: "Business Strategy" 
  },
  { 
    jargon: "leverage", 
    explanation: "Strategic utilization of existing assets or capabilities to maximize value creation and competitive advantage", 
    category: "Business Strategy" 
  },
  { 
    jargon: "pivot", 
    explanation: "Strategic business model adjustment based on market feedback to optimize product-market fit and revenue potential", 
    category: "Business Strategy" 
  },
  { 
    jargon: "bandwidth", 
    explanation: "Available organizational capacity for executing initiatives, measured in time, resources, and operational capability", 
    category: "Resource Management" 
  },
  { 
    jargon: "stakeholder", 
    explanation: "Individual or group with vested interest in project outcomes, requiring strategic communication and expectation management", 
    category: "Project Management" 
  },
  { 
    jargon: "deliverable", 
    explanation: "Tangible project output meeting specified requirements and quality standards within defined timeline constraints", 
    category: "Project Management" 
  },
  { 
    jargon: "scope creep", 
    explanation: "Uncontrolled expansion of project requirements beyond original specifications, impacting timeline and resource allocation", 
    category: "Project Management" 
  },
  { 
    jargon: "KPI", 
    explanation: "Key Performance Indicator - quantifiable metric measuring organizational progress toward strategic objectives", 
    category: "Analytics" 
  },
  
  // AI & Machine Learning
  { 
    jargon: "machine learning", 
    explanation: "Algorithmic approach enabling systems to improve performance through pattern recognition and statistical inference from data", 
    category: "Artificial Intelligence" 
  },
  { 
    jargon: "artificial intelligence", 
    explanation: "Computer systems performing tasks typically requiring human intelligence, including reasoning, learning, and decision-making", 
    category: "Artificial Intelligence" 
  },
  { 
    jargon: "deep learning", 
    explanation: "Neural network architecture with multiple layers enabling complex pattern recognition and predictive modeling", 
    category: "Artificial Intelligence" 
  },
  { 
    jargon: "natural language processing", 
    explanation: "AI capability enabling computers to understand, interpret, and generate human language for automated communication", 
    category: "Artificial Intelligence" 
  },
  
  // Security & Compliance
  { 
    jargon: "zero trust", 
    explanation: "Security framework requiring identity verification for every access request, regardless of location or previous authentication", 
    category: "Cybersecurity" 
  },
  { 
    jargon: "penetration testing", 
    explanation: "Authorized security assessment simulating cyber attacks to identify vulnerabilities and evaluate defense effectiveness", 
    category: "Cybersecurity" 
  },
  { 
    jargon: "vulnerability", 
    explanation: "Security weakness in systems or processes that could be exploited to compromise confidentiality, integrity, or availability", 
    category: "Cybersecurity" 
  },
  { 
    jargon: "encryption", 
    explanation: "Cryptographic protection of data through algorithmic transformation, ensuring confidentiality during storage and transmission", 
    category: "Cybersecurity" 
  },
  
  // Data & Analytics
  { 
    jargon: "big data", 
    explanation: "Large, complex datasets requiring specialized technologies for storage, processing, and analysis to extract business insights", 
    category: "Data Science" 
  },
  { 
    jargon: "data warehouse", 
    explanation: "Centralized repository storing integrated data from multiple sources, optimized for analytical queries and business intelligence", 
    category: "Data Architecture" 
  },
  { 
    jargon: "ETL", 
    explanation: "Extract, Transform, Load - data integration process combining information from multiple sources into unified analytical format", 
    category: "Data Engineering" 
  },
  { 
    jargon: "blockchain", 
    explanation: "Distributed ledger technology providing immutable, transparent record-keeping through cryptographic hashing and consensus mechanisms", 
    category: "Emerging Technology" 
  },
  
  // DevOps & Operations
  { 
    jargon: "DevOps", 
    explanation: "Making developers and IT ops play nice together so they stop blaming each other when things break. It's like couples therapy for code", 
    category: "Software Delivery" 
  },
  { 
    jargon: "CI/CD", 
    explanation: "Continuous Integration/Continuous Deployment - automated pipeline ensuring code quality and rapid, reliable software releases", 
    category: "Software Delivery" 
  },
  { 
    jargon: "infrastructure as code", 
    explanation: "Managing computing infrastructure through machine-readable definition files rather than manual hardware configuration", 
    category: "DevOps" 
  },
  { 
    jargon: "observability", 
    explanation: "System monitoring capability providing insights into internal states through metrics, logs, and distributed tracing", 
    category: "Operations" 
  }
];

export function findTranslation(input: string): Translation | null {
  const cleanInput = input.toLowerCase().trim();
  
  // Direct match
  const directMatch = techTranslations.find(t => 
    t.jargon.toLowerCase() === cleanInput
  );
  
  if (directMatch) return directMatch;
  
  // Fuzzy match - check for partial matches
  const fuzzyMatch = techTranslations.find(t => 
    cleanInput.includes(t.jargon.toLowerCase()) || 
    t.jargon.toLowerCase().includes(cleanInput)
  );
  
  return fuzzyMatch || null;
}

export function getRandomTranslation(): Translation {
  return techTranslations[Math.floor(Math.random() * techTranslations.length)];
}

export function generateFallbackResponse(input: string): string {
  const responses = [
    `"${input}" - Ah, the classic "I have no idea what this means but it sounds important" term. Our AI is scratching its digital head trying to figure this one out. 🤔`,
    `"${input}" - *cricket sounds* Even our AI is like "bro, you're gonna need to be more specific." Maybe try speaking in human? 😅`,
    `"${input}" - Our AI just blinked twice and said "error 404: translation not found." This is peak tech jargon right here. 🚀`,
    `"${input}" - *AI processing noises* "Loading... loading... still loading... okay, this is definitely a thing that exists somewhere." 🤖`,
    `"${input}" - Our AI's response: "I'm not saying it's aliens, but... it's probably aliens." 👽` 
  ];
  
  return responses[Math.floor(Math.random() * responses.length)];
} 