import asyncio
import sys
from agents.orchestrator import ScholarAgentOrchestrator
import database

async def main():
    print("=" * 60)
    print(" Global Scholar Agent - Multi-Agent Portal ")
    print("=" * 60)
    
    database.initialize_dbs()
    orchestrator = ScholarAgentOrchestrator()
    
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        response = await orchestrator.execute_task(prompt)
        print("\n=== Matched Recommendations ===")
        print(response["result"])
        print("=" * 60)
        return

    print("Type your academic profile details (e.g. 'I want to study Computer Science in Germany, my GPA is 3.5, IELTS is 7.5' or 'exit'):")
    while True:
        try:
            prompt = input("\nScholarAgent> ").strip()
            if not prompt:
                continue
            if prompt.lower() in ["exit", "quit"]:
                print("Exiting Global Scholar Portal. Best of luck with your applications!")
                break
                
            response = await orchestrator.execute_task(prompt)
            print("\n=== Recommendations & Report ===")
            print(response["result"])
            print("=" * 60)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
