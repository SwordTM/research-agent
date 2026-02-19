
import { NextResponse } from 'next/server';

export async function GET() {
    const encoder = new TextEncoder();

    const stream = new ReadableStream({
        async start(controller) {
            const sendEvent = (data: any) => {
                controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
            };

            sendEvent({ type: 'log', message: 'Starting mock visualization test...' });
            await new Promise(resolve => setTimeout(resolve, 500));

            sendEvent({ type: 'log', message: 'Generating test slide...' });
            await new Promise(resolve => setTimeout(resolve, 500));

            // Return a path to an existing slide or a placeholder
            // Assuming public/slides/example.html exists or similar
            sendEvent({
                type: 'complete',
                data: {
                    concepts: [
                        {
                            id: 'test-concept',
                            slide_url: '/slides/example.html'
                        }
                    ]
                }
            });

            controller.close();
        },
    });

    return new NextResponse(stream, {
        headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        },
    });
}
