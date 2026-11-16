import { NextRequest } from "next/server";

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";
const FORWARDED_HEADERS = ["content-type", "x-request-id"];

async function forward(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const target = new URL(`/api/${path.map(encodeURIComponent).join("/")}`, API_URL);
  target.search = request.nextUrl.search;

  const headers = new Headers();
  for (const name of FORWARDED_HEADERS) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  if (process.env.API_KEY) headers.set("x-api-key", process.env.API_KEY);

  const hasBody = !["GET", "HEAD"].includes(request.method);
  try {
    const upstream = await fetch(target, {
      method: request.method,
      headers,
      body: hasBody ? await request.text() : undefined,
      cache: "no-store",
      signal: AbortSignal.timeout(10_000),
    });
    return new Response(upstream.status === 204 ? null : upstream.body, {
      status: upstream.status,
      headers: {
        "content-type": upstream.headers.get("content-type") ?? "application/json",
        "x-request-id": upstream.headers.get("x-request-id") ?? "",
      },
    });
  } catch {
    return Response.json({ detail: "The portfolio service is not reachable right now." }, { status: 502 });
  }
}

export { forward as GET, forward as POST, forward as PUT, forward as DELETE };
