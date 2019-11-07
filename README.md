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
5. Zwiększenie liczby pracowników niezawsze zwiększa liniowo czas wykonania zadania. Funkcja czasu trwania zadania od liczy przydzielonych zasobów może być liniowa, wklęsła lub wypukła.

#### Generator zadań
Stoworzno generator zadań zgodny z założeniami przedstawionymi we wstępie. Generuje on listę zadań na podstawie zadanych parametrów:
- liczba zadań
- zakresy rozkłady symulującego bimodalny
- proporcja długich zadań do krótkich
- średni czas odstępu pomiędzy zadaniami
Uruchomienie generatora powoduje wygenerowanie listy zadań o długościach z zadanego rozkłądu bimodalnego i odstępach z zadanego rozkładu normalnego. Wygenerowaną listę obiektów, można zapisać do pliku, aby przeprowadzić testy działania wielu algorytmów szeregowania na jednakowym zestawie zadań.

#### Algorytmy
Opracowano trzy algorytmy szeregujące zadania. Kolejne algorytmy zwiększają stopień równoległości wykonania zadań oraz reprezentują inne sposoby rozwiązania problemu:
1. Szeregowy - pierwszy algorytm przydziela zadaniu zasoby wtedy i tylko wtedy, gdy można zadaniu przydzielić minimum z maksymalnych żądanych zasobów i całkowitej liczby zasobów. Jeśli nie można przydzielić zadania zostaje ono zakolejkowane i czeka na zwolnienie zasobów. Kolejka jest sortowana według długości wykonania zadania przy użyciu jednego zasobu, tak aby najkrótsze zadania były wykonane pierwsze. Takie podejście minimalizuje czas przetwarzania każdego zadania, poniważ jest ono wykonywanie zawsze za pomocą maksymalnej liczby zasobów, jednak wiele zadań musi czekać w kolejce na ich wykonanie.
2. Szeregowy z podziałem na dwie kolejki - jest to modyfikacja pierwszego algorytmu polegająca na utworzeniu dwóch kolejek oraz podzieleniu zasobów na dwie pule. Jedna pula zasobów oraz kolejka jest dedykowana do przetwarzania krótkch zadań, a druga do przetwarzania długich zadań. Zadania wewnątrz danej puli i kolejki są przetwarzane zgodnie z pierwszym algorytmem. Pozawala to oddzielić krótkie zadania od długich i uniknięcie głodzenia niektórych zadań będących w kolejce.
3. Sprawiedliwy - w tym algorytmie każde zadanie zgłaszające żądanie przydzielenia zasobów otrzyma conajmniej jeden zasób, jeśli liczba zadań wykonywanych jest mniejsza niż całkowita liczba zasobów. Jeśli w momencie zgłoszenia wszytkie zasoby są przydzielone do już wykonywanych zadań następuje wywłaszczenie odpwiedniej liczby zadań z pewnej liczby zasobów, tak aby każde zadanie posiadało równą liczbę zasobów. Aby rozwiązać sytuacje gdy liczba zasobów nie jest podzielna, przez liczbę wykonywanych zadań przydzielanie zasobów jest wykonywane algorytmem Round Robin, w którym uszeregowanie zadań do przydziału zasobów jest względem ich starszeństwa.

#### Teza
Algorytm szeregowy powinien minimalizować sumy czasów przetwarzania zadań od ich rozpoczęcia do zakończenia, lecz kosztem wydłużenia sumarycznego czasu przetwarzania wszystkich zadań. Algorym sprawiedliwy wydłuża sumy wykonywania czasów zadań, lecz minimalizuje sume czasu wykonania wszystkich zadań. Algorym szeregowy z podziałem na dwie kolejki powinien osiągać wyniki znajdujace sie pomiędzy dwoma poprzednimi algorytmami w obydwu minimalizowanych metrykach.
