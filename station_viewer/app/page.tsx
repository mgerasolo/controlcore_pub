import Link from "next/link";

export default function Home() {
  return (
    <main className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">ControlCore Dashboard</h1>
      <ul className="list-disc list-inside space-y-2">
        <li>
          <Link href="/station" className="text-blue-600 underline">
            Station Viewer
          </Link>
        </li>
        <li>
          <Link href="/ai" className="text-blue-600 underline">
            Control AI Status
          </Link>
        </li>
      </ul>
    </main>
  );
}
