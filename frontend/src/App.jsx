import Sidebar from "./components/Sidebar"
import ChatArea from "./components/ChatArea"
import Header from "./components/Header"

export default function App() {
  return (
    <div className="h-screen flex bg-gray-950 text-gray-100">

      {/* Sidebar */}
      <div className="w-72 bg-gray-900 border-r border-gray-800">
        <Sidebar />
      </div>

      {/* Main Area */}
      <div className="flex-1 flex flex-col bg-gray-950">

        {/* Header */}
        <div className="h-16 bg-gray-900 border-b border-gray-800">
          <Header />
        </div>

        {/* Chat Area */}
        <div className="flex-1 p-6 overflow-hidden">
          <ChatArea />
        </div>

      </div>
    </div>
  )
}


