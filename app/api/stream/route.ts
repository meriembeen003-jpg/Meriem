import {
  getSentinelTelemetry,
  subscribeSentinelSse,
} from "@/lib/server/sentinel-engine";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    start(controller) {
      const sendEvent = (eventName: string, data: unknown) => {
        try {
          controller.enqueue(
            encoder.encode(
              `event: ${eventName}\ndata: ${JSON.stringify(data)}\n\n`
            )
          );
        } catch {
          // Stream closed
        }
      };

      // Initial handshake
      sendEvent("connected", getSentinelTelemetry());

      const unsubscribe = subscribeSentinelSse((eventName, payload) => {
        sendEvent(eventName, payload);
      });

      req.signal.addEventListener("abort", () => {
        unsubscribe();
        try {
          controller.close();
        } catch {
          // Ignore already closed
        }
      });
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "Access-Control-Allow-Origin": "*",
    },
  });
}
