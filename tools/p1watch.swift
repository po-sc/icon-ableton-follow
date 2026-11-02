// p1watch: только слушает порты iCON (ничего не отправляет) и пишет в лог,
// когда устройство пропало из системы или вернулось. Показывает активность по минутам.
// Молчание само по себе не значит зависание: без нажатий контроллер может ничего не слать.
// Запуск: swiftc -O tools/p1watch.swift -o /tmp/p1watch && /tmp/p1watch p1watch.log
import CoreMIDI
import Foundation

let logPath = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "p1watch.log"

func name(_ e: MIDIEndpointRef) -> String {
    var s: Unmanaged<CFString>?
    MIDIObjectGetStringProperty(e, kMIDIPropertyDisplayName, &s)
    return s?.takeRetainedValue() as String? ?? "?"
}
let fmt = DateFormatter(); fmt.dateFormat = "yyyy-MM-dd HH:mm:ss"
func log(_ m: String) {
    let line = "\(fmt.string(from: Date())) \(m)\n"
    print(line, terminator: "")
    if let h = FileHandle(forWritingAtPath: logPath) {
        h.seekToEndOfFile(); h.write(line.data(using: .utf8)!); h.closeFile()
    } else {
        FileManager.default.createFile(atPath: logPath, contents: line.data(using: .utf8))
    }
}

let lock = NSLock()
var counts: [String: Int] = [:]
var connected: [MIDIEndpointRef: String] = [:]

var client = MIDIClientRef()
MIDIClientCreateWithBlock("p1watch" as CFString, &client) { _ in }
var inPort = MIDIPortRef()
MIDIInputPortCreateWithBlock(client, "in" as CFString, &inPort) { list, src in
    let port = Unmanaged<NSString>.fromOpaque(src!).takeUnretainedValue() as String
    var count = 0
    for _ in list.unsafeSequence() { count += 1 }
    lock.lock()
    counts[port, default: 0] += count
    lock.unlock()
}

func refresh() {
    var present: [MIDIEndpointRef: String] = [:]
    for i in 0..<MIDIGetNumberOfSources() {
        let e = MIDIGetSource(i), n = name(e)
        if n.contains("P1") || n.contains("iCON") { present[e] = n }
    }
    for (e, n) in present where connected[e] == nil {
        let ref = Unmanaged.passRetained(n as NSString).toOpaque()
        MIDIPortConnectSource(inPort, e, ref)
        log("ПОРТ ПОЯВИЛСЯ: \(n)")
    }
    for (e, n) in connected where present[e] == nil {
        log("ПОРТ ПРОПАЛ (устройство отвалилось от USB): \(n)")
    }
    connected = present
}

log("старт p1watch")
refresh()
var ticks = 0
Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
    refresh()
    ticks += 1
    if ticks % 60 == 0 {
        lock.lock()
        let summary = counts.keys.sorted().map { "\($0): пакетов \(counts[$0]!)" }.joined(separator: "; ")
        counts = [:]
        lock.unlock()
        log("на связи, портов \(connected.count) | \(summary.isEmpty ? "нажатий не было" : summary)")
    }
}
RunLoop.main.run()
