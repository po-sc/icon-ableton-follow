// color_test: 20 секунд показывает на контроллере 8 цветов и надписи COLOR 1..8,
// затем всё гасит. Отвечает на вопрос, умеет ли экран показывать цвета дорожек.
// Перед запуском закрыть Ableton, контроллер переключить на слот DAW 1 (Порт 1).
// Запуск: swift tools/color_test.swift          (порт "Порт 1")
//         swift tools/color_test.swift "Port 1"  (другое имя порта)
//         swift tools/color_test.swift --list    (только показать порты)
import CoreMIDI
import Foundation

func name(_ e: MIDIEndpointRef) -> String {
    var s: Unmanaged<CFString>?
    MIDIObjectGetStringProperty(e, kMIDIPropertyDisplayName, &s)
    return s?.takeRetainedValue() as String? ?? "?"
}

let argument = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "Порт 1"
let destinations = (0..<MIDIGetNumberOfDestinations()).map { MIDIGetDestination($0) }

if argument == "--list" {
    destinations.forEach { print(name($0)) }
    exit(0)
}
guard let target = destinations.first(where: { name($0).contains(argument) && (name($0).contains("P1") || name($0).contains("iCON")) }) else {
    print("Порт с именем \"\(argument)\" не найден. Есть:")
    destinations.forEach { print("  " + name($0)) }
    exit(1)
}

var client = MIDIClientRef()
MIDIClientCreateWithBlock("color_test" as CFString, &client) { _ in }
var port = MIDIPortRef()
MIDIOutputPortCreate(client, "out" as CFString, &port)

func send(_ bytes: [UInt8]) {
    var list = MIDIPacketList()
    let packet = MIDIPacketListInit(&list)
    _ = MIDIPacketListAdd(&list, MemoryLayout<MIDIPacketList>.size, packet, 0, bytes.count, bytes)
    MIDISend(port, target, &list)
}

let colorHeader: [UInt8] = [0xF0, 0x00, 0x02, 0x4E, 0x16, 0x14]
let namesHeader: [UInt8] = [0xF0, 0x00, 0x00, 0x66, 0x14, 0x12, 0x00]
let colors: [[UInt8]] = [
    [127, 0, 0], [127, 60, 0], [127, 127, 0], [0, 127, 0],
    [0, 127, 127], [0, 0, 127], [80, 0, 127], [127, 127, 127],
]

func show(names: String, rgb: [[UInt8]]) {
    send(colorHeader + rgb.flatMap { $0 } + [0xF7])
    send(namesHeader + Array(names.padding(toLength: 56, withPad: " ", startingAt: 0).utf8) + [0xF7])
}

print("Отправляю в: \(name(target)). Смотри на экран контроллера 20 секунд.")
let labels = (1...8).map { "COLOR \($0)" }.joined()
for _ in 0..<80 {
    show(names: labels, rgb: colors)
    Thread.sleep(forTimeInterval: 0.25)
}
show(names: "", rgb: Array(repeating: [0, 0, 0], count: 8))
print("Готово, экран очищен.")
print("Есть надписи и цвета: цвета поддерживаются.")
print("Есть только надписи: связь есть, а цвета этот экран не показывает.")
print("Нет ничего: контроллер не на слоте DAW 1 или экран не отвечает на эти команды.")
