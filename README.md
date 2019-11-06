# Szeregowanie Zadań
### Pracownia badawczo-naukowa

------------

#### Abstract
Szeregowanie zadań to szeroko znany i ważny problem, który odpowiada wielu problemom isteniejącym w codziennym życiu. Zależnie od przyjętch założeń, można stworzyć wiele algorytmów przydzielajacych zadania do zasobów, aby zoptmalizować zadaną metrtykę, np. średni czas przetwarzania zadania, suma opoźnień zadań. W ramach stworzonego projektu zostały stworzone trzy algorymty reprezentujące różne podejścia do problemu szeregowania. Zależnie od przyjętej funkcji celu (metryki) inne algorytmy tworzą najlepsze rozwiązania.

#### Wstęp
Problem szeregowania zadań można przedstawić na przykładzie firmy zajmującej się kopaniem rowów. Jej zasobami są pracownicy, a zadaniami rowy do wykopania. Aby zamodelować rzeczywiste problemy takiej firmy i jej przydziału pracowników do zadań przyjęto następujace założenia:
1. Dane zadanie musi być wykonywanie przez określoną minimalną liczbę pracowników (zasobów), aby możliwe było jego rozpoczęcie. Odpowiada to pracom zbyt skomplikowanym, aby były wykonywane przez jedną osobę lub mały zespół. W uproszczonej wersji problemu założono, że każde zadanie może być wykonywane również przez tylko jedną osobę.
2. Dane zadanie może być wykonywanie przez określoną maksymalną liczbę pracowinków. Odpowiada to sytuacjom, gdy każdy kolejny pracownik, nie przyspiesza postępu prac, gdzyż wszystkie stanowiska pracy są obsadzone i nie da dalej się zrównoleglać problemu.
3. Odstępy pomiędzy zgłoszeniami pochodzą z rozkładu normalnego, aby zamodelować prawdopodony tępo zgłoszeń, jakie może wystąpić w przeciętnej firmie.
4. Czasy trwania zadań pochodzą z rozkładu przypominającego rozkłąd dwumodalny. Pozwala to uzyskać zarówna zadania krótkie, jak i bardzo długie, co lepiej modeluje rzeczywistość i pozwala zbadać zachowanie systemu w skrajnych sytuacjach.

#### Algorytmy
Opracowano trzy algorytmy, które stopniowo zwiększają stopeń równołości wykonania zadań.
