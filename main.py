import concurrent.futures
import threading
import random
import asyncio

alunos = {
    12345: ("Pedro", 9.5),
    23456: ("Paulo", 7.8),
    34567: ("Agatha", 6.2),
    45678: ("Leonanrdo", 8.9),
    56789: ("Patricia", 9.0),
    67890: ("Andressa", 7.0),
    78901: ("Alessadra", 5.5),
    89012: ("Leila", 10.0),
    90123: ("Marcio", 4.3),
    11234: ("Matheus", 6.7)
}


def get_record_by_id(matricula):
    future = concurrent.futures.Future()
    record = alunos.get(matricula)
    timer = threading.Timer(3, lambda: future.set_result(record))
    timer.start()
    return future


def get_all_records():
    future = concurrent.futures.Future()
    records = list(alunos.items())

    def set_resultado():
        if not future.cancelled():
            future.set_result(records)

    timer = threading.Timer(30, set_resultado)
    timer.start()
    return future



async def generator(limite):
    total = 0
    while total < limite:
        yield random.randint(0, 100)
        total += 1


async def player(name, cartela, fila):
    marcados = set()
    while True:
        num = await fila.get()
        print(f"{name} {num} {cartela} {len(marcados)}")
        marcados.add(num)
        if len(marcados) == len(cartela):
            return name, cartela, marcados
    return None, None, None


async def narrator(players, limite):
    filas = [asyncio.Queue() for i in players]

    tasks = []
    for (name, cartela), fila in zip(players, filas):
        task = asyncio.create_task(player(name, cartela, fila))
        tasks.append(task)

    async for num in generator(limite):
        print(f"Number is {num}")

        for fila in filas:
            await fila.put(num)

        await asyncio.sleep(0.01)

        for t in tasks:
            if t.done():
                vencedor = t.result()
                if vencedor[0] is not None:
                    print(f"{vencedor[0]} is the WINNER {vencedor[1]} {vencedor[2]}")
                    for fila in filas:
                        await fila.put(None)
                    return

    print("No winner!")
    for q in filas:
        await q.put(None)


async def bingo_main():
    random.seed()

    jogadores = [
        ("player-1", [5, 10, 48, 55]),
        ("player-2", [8, 46, 80, 99]),
        ("player-3", [17, 29, 78, 95])
    ]

    limite = 1000

    await narrator(jogadores, limite)
    print("Game is over")


if __name__ == "__main__":
    print("================ Parte 1 - Matriculas =============")
    matriculas = [12345, 23456, 34567, 45678, 56789]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        futures.append(get_record_by_id(matriculas[0]))
        futures.append(get_record_by_id(matriculas[1]))
        futures.append(get_record_by_id(matriculas[2]))
        futures.append(get_record_by_id(matriculas[3]))
        futures.append(get_record_by_id(matriculas[4]))
        results = [f.result() for f in futures]
        for mat, (nome, nota) in zip(matriculas, results):
            print(f"Matricula: {mat}, Nome: {nome}, Nota: {nota}")

        notas = [r[1] for r in results]
        media = sum(notas) / len(notas)
        print(f"Media: {media}")

        future_all = get_all_records()

        print("Executando get_all_records()")
        aluno = get_record_by_id(67890)
        aluno_nome, aluno_nota = aluno.result()
        print(f"Matricula: {67890}, Nome: {aluno_nome}, Nota: {aluno_nota}")

        canceled = future_all.cancel()
        if not canceled:
            all_records = future_all.result()
            print(f"get_all_records() não foi cancelado e retornou {len(all_records)} registros.")
        else:
            print(f"get_all_records() foi cancelado!.")

    print("================ Parte 2 - BINGO =============")
    asyncio.run(bingo_main())
