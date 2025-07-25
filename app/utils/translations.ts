export interface Translation {
  jargon: string;
  explanation: string;
  category: string;
}

export const techTranslations: Translation[] = [
  // Development
  { jargon: "refactor", explanation: "Clean up messy code without changing what it does", category: "development" },
  { jargon: "technical debt", explanation: "Shortcuts we took that will bite us later", category: "development" },
  { jargon: "MVP", explanation: "The crappiest version that still works", category: "development" },
  { jargon: "scalable", explanation: "Won't explode when lots of people use it", category: "development" },
  { jargon: "robust", explanation: "Doesn't break when weird stuff happens", category: "development" },
  { jargon: "optimize", explanation: "Make it faster and less wasteful", category: "development" },
  { jargon: "legacy code", explanation: "Old code nobody wants to touch", category: "development" },
  { jargon: "code review", explanation: "Letting others judge your work", category: "development" },
  { jargon: "hotfix", explanation: "Emergency band-aid for broken stuff", category: "development" },
  { jargon: "rollback", explanation: "Undo everything and pretend it never happened", category: "development" },
  
  // Architecture
  { jargon: "microservices", explanation: "Splitting one big app into tiny apps that talk to each other", category: "architecture" },
  { jargon: "monolith", explanation: "One giant app that does everything", category: "architecture" },
  { jargon: "load balancer", explanation: "Traffic cop for your servers", category: "architecture" },
  { jargon: "API", explanation: "A way for apps to talk to each other", category: "architecture" },
  { jargon: "containerization", explanation: "Putting apps in boxes so they work everywhere", category: "architecture" },
  { jargon: "orchestration", explanation: "Managing all those boxes automatically", category: "architecture" },
  
  // Business
  { jargon: "synergy", explanation: "When 1+1 somehow equals 3", category: "business" },
  { jargon: "leverage", explanation: "Use this thing to make that thing better", category: "business" },
  { jargon: "pivot", explanation: "We're changing direction because this isn't working", category: "business" },
  { jargon: "bandwidth", explanation: "How much stuff someone can handle right now", category: "business" },
  { jargon: "stakeholder", explanation: "People who care if this succeeds or fails", category: "business" },
  { jargon: "deliverable", explanation: "Stuff we promised to finish", category: "business" },
  { jargon: "scope creep", explanation: "When the project keeps getting bigger", category: "business" },
  { jargon: "KPI", explanation: "Numbers that tell us if we're winning or losing", category: "business" },
  
  // Modern Tech
  { jargon: "machine learning", explanation: "Teaching computers to guess really well", category: "ai" },
  { jargon: "artificial intelligence", explanation: "Making computers pretend to be smart", category: "ai" },
  { jargon: "blockchain", explanation: "A fancy spreadsheet nobody can cheat on", category: "crypto" },
  { jargon: "cloud computing", explanation: "Using someone else's computer", category: "infrastructure" },
  { jargon: "serverless", explanation: "There are still servers, you just don't see them", category: "infrastructure" },
  { jargon: "edge computing", explanation: "Doing the thinking closer to where you are", category: "infrastructure" },
  
  // Security
  { jargon: "zero trust", explanation: "Trust nobody, verify everything", category: "security" },
  { jargon: "penetration testing", explanation: "Hiring hackers to break your stuff first", category: "security" },
  { jargon: "vulnerability", explanation: "A way bad guys could break in", category: "security" },
  { jargon: "encryption", explanation: "Scrambling data so only the right people can read it", category: "security" },
];

export function findTranslation(input: string): Translation | null {
  const cleanInput = input.toLowerCase().trim();
  
  // Direct match
  const directMatch = techTranslations.find(t => 
    t.jargon.toLowerCase() === cleanInput
  );
  
  if (directMatch) return directMatch;
  
  // Fuzzy match
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
    `Hmm, "${input}" sounds very technical! Let me swim around and think about that one.`,
    `That's some advanced jargon! Even us tech fish need time to decode "${input}".`,
    `Blub blub! "${input}" isn't in my fishionary yet, but it sounds important!`,
    `Swimming through my knowledge base... "${input}" seems like something humans say to sound smart.`,
    `As a wise goldfish once said: "${input}" probably means "it's complicated" in human speak.`
  ];
  
  return responses[Math.floor(Math.random() * responses.length)];
} 